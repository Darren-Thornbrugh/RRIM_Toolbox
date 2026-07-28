# -*- coding: utf-8 -*-
# --------------------------------------------------------------
# RRIM_Toolbox.pyt
# Author: Darren J. Thornbrugh
# Organization: USDA Forest Service
# Description: ArcGIS Pro Python Toolbox for Red Relief Image Map,
#               Openness, Slope, and Terrain Visualization Tools.
# Last Updated: 2026-07-27
# --------------------------------------------------------------


import arcpy
import os
import numpy as np
from osgeo import gdal
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

class Toolbox(object):
    def __init__(self):
        self.label = "Red Relief Tools"
        self.alias = "rrim_tools"
        self.tools = [
            TopographicOpennessIndex,
            SlopeFromDEM,
            RedReliefImageMap,
            RedReliefImageMapClassic
        ]

CIVIDIS_STOPS_STRING = "0.0039063;0,33,78,255,rgb:0,0.1294118,0.3058824,1;rgb;ccw:0.0078125;0,34,80,255,rgb:0,0.1333333,0.3137255,1;rgb;ccw:0.0117188;0,34,82,255,rgb:0,0.1333333,0.3215686,1;rgb;ccw:0.015625;0,35,83,255,rgb:0,0.1372549,0.3254902,1;rgb;ccw:0.0195313;0,36,85,255,rgb:0,0.1411765,0.3333333,1;rgb;ccw:0.0234375;0,37,87,255,rgb:0,0.145098,0.3411765,1;rgb;ccw:0.0273438;0,37,88,255,rgb:0,0.145098,0.345098,1;rgb;ccw:0.03125;0,38,90,255,rgb:0,0.1490196,0.3529412,1;rgb;ccw:0.0351563;0,39,92,255,rgb:0,0.1529412,0.3607843,1;rgb;ccw:0.0390625;0,39,94,255,rgb:0,0.1529412,0.3686275,1;rgb;ccw:0.0429688;0,40,96,255,rgb:0,0.1568627,0.3764706,1;rgb;ccw:0.046875;0,41,97,255,rgb:0,0.1607843,0.3803922,1;rgb;ccw:0.0507813;0,42,99,255,rgb:0,0.1647059,0.3882353,1;rgb;ccw:0.0546875;0,42,101,255,rgb:0,0.1647059,0.3960784,1;rgb;ccw:0.0585938;0,43,103,255,rgb:0,0.1686275,0.4039216,1;rgb;ccw:0.0625;0,44,105,255,rgb:0,0.172549,0.4117647,1;rgb;ccw:0.0664063;0,44,106,255,rgb:0,0.172549,0.4156863,1;rgb;ccw:0.0703125;0,45,108,255,rgb:0,0.1764706,0.4235294,1;rgb;ccw:0.0742188;0,46,110,255,rgb:0,0.1803922,0.4313725,1;rgb;ccw:0.078125;0,46,111,255,rgb:0,0.1803922,0.4352941,1;rgb;ccw:0.0820313;0,47,111,255,rgb:0,0.1843137,0.4352941,1;rgb;ccw:0.0859375;0,47,111,255,rgb:0,0.1843137,0.4352941,1;rgb;ccw:0.0898438;0,48,111,255,rgb:0,0.1882353,0.4352941,1;rgb;ccw:0.09375;0,48,111,255,rgb:0,0.1882353,0.4352941,1;rgb;ccw:0.0976563;0,49,111,255,rgb:0,0.1921569,0.4352941,1;rgb;ccw:0.101563;0,50,111,255,rgb:0,0.1960784,0.4352941,1;rgb;ccw:0.105469;0,51,111,255,rgb:0,0.2,0.4352941,1;rgb;ccw:0.109375;0,51,111,255,rgb:0,0.2,0.4352941,1;rgb;ccw:0.113281;0,52,111,255,rgb:0,0.2039216,0.4352941,1;rgb;ccw:0.117188;0,53,110,255,rgb:0,0.2078431,0.4313725,1;rgb;ccw:0.121094;1,54,110,255,rgb:0.0039216,0.2117647,0.4313725,1;rgb;ccw:0.125;6,54,110,255,rgb:0.0235294,0.2117647,0.4313725,1;rgb;ccw:0.128906;11,55,110,255,rgb:0.0431373,0.2156863,0.4313725,1;rgb;ccw:0.132813;15,56,110,255,rgb:0.0588235,0.2196078,0.4313725,1;rgb;ccw:0.136719;18,56,109,255,rgb:0.0705882,0.2196078,0.427451,1;rgb;ccw:0.140625;21,57,109,255,rgb:0.0823529,0.2235294,0.427451,1;rgb;ccw:0.144531;24,58,109,255,rgb:0.0941176,0.227451,0.427451,1;rgb;ccw:0.148438;26,59,109,255,rgb:0.1019608,0.2313725,0.427451,1;rgb;ccw:0.152344;29,59,109,255,rgb:0.1137255,0.2313725,0.427451,1;rgb;ccw:0.15625;31,60,109,255,rgb:0.1215686,0.2352941,0.427451,1;rgb;ccw:0.160156;33,61,109,255,rgb:0.1294118,0.2392157,0.427451,1;rgb;ccw:0.164063;35,62,108,255,rgb:0.1372549,0.2431373,0.4235294,1;rgb;ccw:0.167969;36,62,108,255,rgb:0.1411765,0.2431373,0.4235294,1;rgb;ccw:0.171875;38,63,108,255,rgb:0.1490196,0.2470588,0.4235294,1;rgb;ccw:0.175781;40,64,108,255,rgb:0.1568627,0.2509804,0.4235294,1;rgb;ccw:0.179688;42,64,108,255,rgb:0.1647059,0.2509804,0.4235294,1;rgb;ccw:0.183594;43,65,108,255,rgb:0.1686275,0.254902,0.4235294,1;rgb;ccw:0.1875;45,66,108,255,rgb:0.1764706,0.2588235,0.4235294,1;rgb;ccw:0.191406;46,67,108,255,rgb:0.1803922,0.2627451,0.4235294,1;rgb;ccw:0.195313;48,67,108,255,rgb:0.1882353,0.2627451,0.4235294,1;rgb;ccw:0.199219;49,68,107,255,rgb:0.1921569,0.2666667,0.4196078,1;rgb;ccw:0.203125;50,69,107,255,rgb:0.1960784,0.2705882,0.4196078,1;rgb;ccw:0.207031;52,69,107,255,rgb:0.2039216,0.2705882,0.4196078,1;rgb;ccw:0.210938;53,70,107,255,rgb:0.2078431,0.2745098,0.4196078,1;rgb;ccw:0.214844;54,71,107,255,rgb:0.2117647,0.2784314,0.4196078,1;rgb;ccw:0.21875;56,72,107,255,rgb:0.2196078,0.2823529,0.4196078,1;rgb;ccw:0.222656;57,72,107,255,rgb:0.2235294,0.2823529,0.4196078,1;rgb;ccw:0.226563;58,73,107,255,rgb:0.227451,0.2862745,0.4196078,1;rgb;ccw:0.230469;59,74,107,255,rgb:0.2313725,0.2901961,0.4196078,1;rgb;ccw:0.234375;61,74,107,255,rgb:0.2392157,0.2901961,0.4196078,1;rgb;ccw:0.238281;62,75,107,255,rgb:0.2431373,0.2941176,0.4196078,1;rgb;ccw:0.242188;63,76,107,255,rgb:0.2470588,0.2980392,0.4196078,1;rgb;ccw:0.246094;64,77,107,255,rgb:0.2509804,0.3019608,0.4196078,1;rgb;ccw:0.25;65,77,107,255,rgb:0.254902,0.3019608,0.4196078,1;rgb;ccw:0.253906;66,78,107,255,rgb:0.2588235,0.3058824,0.4196078,1;rgb;ccw:0.257813;67,79,107,255,rgb:0.2627451,0.3098039,0.4196078,1;rgb;ccw:0.261719;68,79,107,255,rgb:0.2666667,0.3098039,0.4196078,1;rgb;ccw:0.265625;70,80,107,255,rgb:0.2745098,0.3137255,0.4196078,1;rgb;ccw:0.269531;71,81,107,255,rgb:0.2784314,0.3176471,0.4196078,1;rgb;ccw:0.273438;72,82,107,255,rgb:0.2823529,0.3215686,0.4196078,1;rgb;ccw:0.277344;73,82,107,255,rgb:0.2862745,0.3215686,0.4196078,1;rgb;ccw:0.28125;74,83,107,255,rgb:0.2901961,0.3254902,0.4196078,1;rgb;ccw:0.285156;75,84,108,255,rgb:0.2941176,0.3294118,0.4235294,1;rgb;ccw:0.289063;76,84,108,255,rgb:0.2980392,0.3294118,0.4235294,1;rgb;ccw:0.292969;77,85,108,255,rgb:0.3019608,0.3333333,0.4235294,1;rgb;ccw:0.296875;78,86,108,255,rgb:0.3058824,0.3372549,0.4235294,1;rgb;ccw:0.300781;79,87,108,255,rgb:0.3098039,0.3411765,0.4235294,1;rgb;ccw:0.304688;80,87,108,255,rgb:0.3137255,0.3411765,0.4235294,1;rgb;ccw:0.308594;81,88,108,255,rgb:0.3176471,0.345098,0.4235294,1;rgb;ccw:0.3125;82,89,108,255,rgb:0.3215686,0.3490196,0.4235294,1;rgb;ccw:0.316406;83,89,108,255,rgb:0.3254902,0.3490196,0.4235294,1;rgb;ccw:0.320313;84,90,108,255,rgb:0.3294118,0.3529412,0.4235294,1;rgb;ccw:0.324219;85,91,109,255,rgb:0.3333333,0.3568627,0.427451,1;rgb;ccw:0.328125;86,92,109,255,rgb:0.3372549,0.3607843,0.427451,1;rgb;ccw:0.332031;87,92,109,255,rgb:0.3411765,0.3607843,0.427451,1;rgb;ccw:0.335938;88,93,109,255,rgb:0.345098,0.3647059,0.427451,1;rgb;ccw:0.339844;89,94,109,255,rgb:0.3490196,0.3686275,0.427451,1;rgb;ccw:0.34375;89,95,109,255,rgb:0.3490196,0.372549,0.427451,1;rgb;ccw:0.347656;90,95,109,255,rgb:0.3529412,0.372549,0.427451,1;rgb;ccw:0.351563;91,96,110,255,rgb:0.3568627,0.3764706,0.4313725,1;rgb;ccw:0.355469;92,97,110,255,rgb:0.3607843,0.3803922,0.4313725,1;rgb;ccw:0.359375;93,97,110,255,rgb:0.3647059,0.3803922,0.4313725,1;rgb;ccw:0.363281;94,98,110,255,rgb:0.3686275,0.3843137,0.4313725,1;rgb;ccw:0.367188;95,99,110,255,rgb:0.372549,0.3882353,0.4313725,1;rgb;ccw:0.371094;96,100,111,255,rgb:0.3764706,0.3921569,0.4352941,1;rgb;ccw:0.375;97,100,111,255,rgb:0.3803922,0.3921569,0.4352941,1;rgb;ccw:0.378906;98,101,111,255,rgb:0.3843137,0.3960784,0.4352941,1;rgb;ccw:0.382813;99,102,111,255,rgb:0.3882353,0.4,0.4352941,1;rgb;ccw:0.386719;100,102,111,255,rgb:0.3921569,0.4,0.4352941,1;rgb;ccw:0.390625;100,103,112,255,rgb:0.3921569,0.4039216,0.4392157,1;rgb;ccw:0.394531;101,104,112,255,rgb:0.3960784,0.4078431,0.4392157,1;rgb;ccw:0.398438;102,105,112,255,rgb:0.4,0.4117647,0.4392157,1;rgb;ccw:0.402344;103,105,112,255,rgb:0.4039216,0.4117647,0.4392157,1;rgb;ccw:0.40625;104,106,113,255,rgb:0.4078431,0.4156863,0.4431373,1;rgb;ccw:0.410156;105,107,113,255,rgb:0.4117647,0.4196078,0.4431373,1;rgb;ccw:0.414063;106,108,113,255,rgb:0.4156863,0.4235294,0.4431373,1;rgb;ccw:0.417969;107,108,113,255,rgb:0.4196078,0.4235294,0.4431373,1;rgb;ccw:0.421875;108,109,114,255,rgb:0.4235294,0.427451,0.4470588,1;rgb;ccw:0.425781;108,110,114,255,rgb:0.4235294,0.4313725,0.4470588,1;rgb;ccw:0.429688;109,110,114,255,rgb:0.427451,0.4313725,0.4470588,1;rgb;ccw:0.433594;110,111,115,255,rgb:0.4313725,0.4352941,0.4509804,1;rgb;ccw:0.4375;111,112,115,255,rgb:0.4352941,0.4392157,0.4509804,1;rgb;ccw:0.441406;112,113,115,255,rgb:0.4392157,0.4431373,0.4509804,1;rgb;ccw:0.445313;113,113,116,255,rgb:0.4431373,0.4431373,0.454902,1;rgb;ccw:0.449219;114,114,116,255,rgb:0.4470588,0.4470588,0.454902,1;rgb;ccw:0.453125;114,115,116,255,rgb:0.4470588,0.4509804,0.454902,1;rgb;ccw:0.457031;115,116,117,255,rgb:0.4509804,0.454902,0.4588235,1;rgb;ccw:0.460938;116,116,117,255,rgb:0.454902,0.454902,0.4588235,1;rgb;ccw:0.464844;117,117,117,255,rgb:0.4588235,0.4588235,0.4588235,1;rgb;ccw:0.46875;118,118,118,255,rgb:0.4627451,0.4627451,0.4627451,1;rgb;ccw:0.472656;119,119,118,255,rgb:0.4666667,0.4666667,0.4627451,1;rgb;ccw:0.476563;120,119,119,255,rgb:0.4705882,0.4666667,0.4666667,1;rgb;ccw:0.480469;120,120,119,255,rgb:0.4705882,0.4705882,0.4666667,1;rgb;ccw:0.484375;121,121,119,255,rgb:0.4745098,0.4745098,0.4666667,1;rgb;ccw:0.488281;122,122,120,255,rgb:0.4784314,0.4784314,0.4705882,1;rgb;ccw:0.492188;123,122,120,255,rgb:0.4823529,0.4784314,0.4705882,1;rgb;ccw:0.496094;124,123,120,255,rgb:0.4862745,0.4823529,0.4705882,1;rgb;ccw:0.5;125,124,120,255,rgb:0.4901961,0.4862745,0.4705882,1;rgb;ccw:0.503906;126,125,120,255,rgb:0.4941176,0.4901961,0.4705882,1;rgb;ccw:0.507813;127,125,120,255,rgb:0.4980392,0.4901961,0.4705882,1;rgb;ccw:0.511719;128,126,121,255,rgb:0.5019608,0.4941176,0.4745098,1;rgb;ccw:0.515625;129,127,121,255,rgb:0.5058824,0.4980392,0.4745098,1;rgb;ccw:0.519531;130,128,121,255,rgb:0.5098039,0.5019608,0.4745098,1;rgb;ccw:0.523438;131,128,121,255,rgb:0.5137255,0.5019608,0.4745098,1;rgb;ccw:0.527344;132,129,121,255,rgb:0.5176471,0.5058824,0.4745098,1;rgb;ccw:0.53125;132,130,121,255,rgb:0.5176471,0.5098039,0.4745098,1;rgb;ccw:0.535156;133,131,121,255,rgb:0.5215686,0.5137255,0.4745098,1;rgb;ccw:0.539063;134,131,121,255,rgb:0.5254902,0.5137255,0.4745098,1;rgb;ccw:0.542969;135,132,121,255,rgb:0.5294118,0.5176471,0.4745098,1;rgb;ccw:0.546875;136,133,121,255,rgb:0.5333333,0.5215686,0.4745098,1;rgb;ccw:0.550781;137,134,121,255,rgb:0.5372549,0.5254902,0.4745098,1;rgb;ccw:0.554688;138,135,121,255,rgb:0.5411765,0.5294118,0.4745098,1;rgb;ccw:0.558594;139,135,121,255,rgb:0.545098,0.5294118,0.4745098,1;rgb;ccw:0.5625;140,136,121,255,rgb:0.5490196,0.5333333,0.4745098,1;rgb;ccw:0.566406;141,137,121,255,rgb:0.5529412,0.5372549,0.4745098,1;rgb;ccw:0.570313;142,138,121,255,rgb:0.5568627,0.5411765,0.4745098,1;rgb;ccw:0.574219;143,138,121,255,rgb:0.5607843,0.5411765,0.4745098,1;rgb;ccw:0.578125;144,139,121,255,rgb:0.5647059,0.545098,0.4745098,1;rgb;ccw:0.582031;145,140,120,255,rgb:0.5686275,0.5490196,0.4705882,1;rgb;ccw:0.585938;146,141,120,255,rgb:0.572549,0.5529412,0.4705882,1;rgb;ccw:0.589844;147,142,120,255,rgb:0.5764706,0.5568627,0.4705882,1;rgb;ccw:0.59375;148,142,120,255,rgb:0.5803922,0.5568627,0.4705882,1;rgb;ccw:0.597656;149,143,120,255,rgb:0.5843137,0.5607843,0.4705882,1;rgb;ccw:0.601563;150,144,120,255,rgb:0.5882353,0.5647059,0.4705882,1;rgb;ccw:0.605469;151,145,120,255,rgb:0.5921569,0.5686275,0.4705882,1;rgb;ccw:0.609375;152,146,120,255,rgb:0.5960784,0.572549,0.4705882,1;rgb;ccw:0.613281;153,146,120,255,rgb:0.6,0.572549,0.4705882,1;rgb;ccw:0.617188;154,147,119,255,rgb:0.6039216,0.5764706,0.4666667,1;rgb;ccw:0.621094;155,148,119,255,rgb:0.6078431,0.5803922,0.4666667,1;rgb;ccw:0.625;156,149,119,255,rgb:0.6117647,0.5843137,0.4666667,1;rgb;ccw:0.628906;157,150,119,255,rgb:0.6156863,0.5882353,0.4666667,1;rgb;ccw:0.632813;158,150,119,255,rgb:0.6196078,0.5882353,0.4666667,1;rgb;ccw:0.636719;159,151,119,255,rgb:0.6235294,0.5921569,0.4666667,1;rgb;ccw:0.640625;160,152,119,255,rgb:0.627451,0.5960784,0.4666667,1;rgb;ccw:0.644531;161,153,118,255,rgb:0.6313725,0.6,0.4627451,1;rgb;ccw:0.648438;162,154,118,255,rgb:0.6352941,0.6039216,0.4627451,1;rgb;ccw:0.652344;163,154,118,255,rgb:0.6392157,0.6039216,0.4627451,1;rgb;ccw:0.65625;164,155,118,255,rgb:0.6431373,0.6078431,0.4627451,1;rgb;ccw:0.660156;165,156,118,255,rgb:0.6470588,0.6117647,0.4627451,1;rgb;ccw:0.664063;166,157,117,255,rgb:0.6509804,0.6156863,0.4588235,1;rgb;ccw:0.667969;168,158,117,255,rgb:0.6588235,0.6196078,0.4588235,1;rgb;ccw:0.671875;169,159,117,255,rgb:0.6627451,0.6235294,0.4588235,1;rgb;ccw:0.675781;170,159,117,255,rgb:0.6666667,0.6235294,0.4588235,1;rgb;ccw:0.679688;171,160,116,255,rgb:0.6705882,0.627451,0.454902,1;rgb;ccw:0.683594;172,161,116,255,rgb:0.6745098,0.6313725,0.454902,1;rgb;ccw:0.6875;173,162,116,255,rgb:0.6784314,0.6352941,0.454902,1;rgb;ccw:0.691406;174,163,116,255,rgb:0.6823529,0.6392157,0.454902,1;rgb;ccw:0.695313;175,164,115,255,rgb:0.6862745,0.6431373,0.4509804,1;rgb;ccw:0.699219;176,164,115,255,rgb:0.6901961,0.6431373,0.4509804,1;rgb;ccw:0.703125;177,165,115,255,rgb:0.6941176,0.6470588,0.4509804,1;rgb;ccw:0.707031;178,166,114,255,rgb:0.6980392,0.6509804,0.4470588,1;rgb;ccw:0.710938;179,167,114,255,rgb:0.7019608,0.654902,0.4470588,1;rgb;ccw:0.714844;180,168,114,255,rgb:0.7058824,0.6588235,0.4470588,1;rgb;ccw:0.71875;181,169,113,255,rgb:0.7098039,0.6627451,0.4431373,1;rgb;ccw:0.722656;182,169,113,255,rgb:0.7137255,0.6627451,0.4431373,1;rgb;ccw:0.726563;183,170,113,255,rgb:0.7176471,0.6666667,0.4431373,1;rgb;ccw:0.730469;184,171,112,255,rgb:0.7215686,0.6705882,0.4392157,1;rgb;ccw:0.734375;185,172,112,255,rgb:0.7254902,0.6745098,0.4392157,1;rgb;ccw:0.738281;186,173,112,255,rgb:0.7294118,0.6784314,0.4392157,1;rgb;ccw:0.742188;187,174,111,255,rgb:0.7333333,0.6823529,0.4352941,1;rgb;ccw:0.746094;188,175,111,255,rgb:0.7372549,0.6862745,0.4352941,1;rgb;ccw:0.75;190,175,111,255,rgb:0.745098,0.6862745,0.4352941,1;rgb;ccw:0.753906;191,176,110,255,rgb:0.7490196,0.6901961,0.4313725,1;rgb;ccw:0.757813;192,177,110,255,rgb:0.7529412,0.6941176,0.4313725,1;rgb;ccw:0.761719;193,178,109,255,rgb:0.7568627,0.6980392,0.427451,1;rgb;ccw:0.765625;194,179,109,255,rgb:0.7607843,0.7019608,0.427451,1;rgb;ccw:0.769531;195,180,109,255,rgb:0.7647059,0.7058824,0.427451,1;rgb;ccw:0.773438;196,181,108,255,rgb:0.7686275,0.7098039,0.4235294,1;rgb;ccw:0.777344;197,181,108,255,rgb:0.772549,0.7098039,0.4235294,1;rgb;ccw:0.78125;198,182,107,255,rgb:0.7764706,0.7137255,0.4196078,1;rgb;ccw:0.785156;199,183,107,255,rgb:0.7803922,0.7176471,0.4196078,1;rgb;ccw:0.789063;200,184,106,255,rgb:0.7843137,0.7215686,0.4156863,1;rgb;ccw:0.792969;201,185,106,255,rgb:0.7882353,0.7254902,0.4156863,1;rgb;ccw:0.796875;203,186,105,255,rgb:0.7960784,0.7294118,0.4117647,1;rgb;ccw:0.800781;204,187,105,255,rgb:0.8,0.7333333,0.4117647,1;rgb;ccw:0.804688;205,188,104,255,rgb:0.8039216,0.7372549,0.4078431,1;rgb;ccw:0.808594;206,188,104,255,rgb:0.8078431,0.7372549,0.4078431,1;rgb;ccw:0.8125;207,189,103,255,rgb:0.8117647,0.7411765,0.4039216,1;rgb;ccw:0.816406;208,190,103,255,rgb:0.8156863,0.745098,0.4039216,1;rgb;ccw:0.820313;209,191,102,255,rgb:0.8196078,0.7490196,0.4,1;rgb;ccw:0.824219;210,192,102,255,rgb:0.8235294,0.7529412,0.4,1;rgb;ccw:0.828125;211,193,101,255,rgb:0.827451,0.7568627,0.3960784,1;rgb;ccw:0.832031;212,194,100,255,rgb:0.8313725,0.7607843,0.3921569,1;rgb;ccw:0.835938;214,195,100,255,rgb:0.8392157,0.7647059,0.3921569,1;rgb;ccw:0.839844;215,196,99,255,rgb:0.8431373,0.7686275,0.3882353,1;rgb;ccw:0.84375;216,197,99,255,rgb:0.8470588,0.772549,0.3882353,1;rgb;ccw:0.847656;217,197,98,255,rgb:0.8509804,0.772549,0.3843137,1;rgb;ccw:0.851563;218,198,97,255,rgb:0.854902,0.7764706,0.3803922,1;rgb;ccw:0.855469;219,199,97,255,rgb:0.8588235,0.7803922,0.3803922,1;rgb;ccw:0.859375;220,200,96,255,rgb:0.8627451,0.7843137,0.3764706,1;rgb;ccw:0.863281;221,201,95,255,rgb:0.8666667,0.7882353,0.372549,1;rgb;ccw:0.867188;222,202,95,255,rgb:0.8705882,0.7921569,0.372549,1;rgb;ccw:0.871094;224,203,94,255,rgb:0.8784314,0.7960784,0.3686275,1;rgb;ccw:0.875;225,204,93,255,rgb:0.8823529,0.8,0.3647059,1;rgb;ccw:0.878906;226,205,92,255,rgb:0.8862745,0.8039216,0.3607843,1;rgb;ccw:0.882813;227,206,92,255,rgb:0.8901961,0.8078431,0.3607843,1;rgb;ccw:0.886719;228,207,91,255,rgb:0.8941176,0.8117647,0.3568627,1;rgb;ccw:0.890625;229,208,90,255,rgb:0.8980392,0.8156863,0.3529412,1;rgb;ccw:0.894531;230,209,89,255,rgb:0.9019608,0.8196078,0.3490196,1;rgb;ccw:0.898438;232,210,89,255,rgb:0.9098039,0.8235294,0.3490196,1;rgb;ccw:0.902344;233,211,88,255,rgb:0.9137255,0.827451,0.345098,1;rgb;ccw:0.90625;234,211,87,255,rgb:0.9176471,0.827451,0.3411765,1;rgb;ccw:0.910156;235,212,86,255,rgb:0.9215686,0.8313725,0.3372549,1;rgb;ccw:0.914063;236,213,85,255,rgb:0.9254902,0.8352941,0.3333333,1;rgb;ccw:0.917969;237,214,84,255,rgb:0.9294118,0.8392157,0.3294118,1;rgb;ccw:0.921875;239,215,83,255,rgb:0.9372549,0.8431373,0.3254902,1;rgb;ccw:0.925781;240,216,82,255,rgb:0.9411765,0.8470588,0.3215686,1;rgb;ccw:0.929688;241,217,81,255,rgb:0.945098,0.8509804,0.3176471,1;rgb;ccw:0.933594;242,218,80,255,rgb:0.9490196,0.854902,0.3137255,1;rgb;ccw:0.9375;243,219,79,255,rgb:0.9529412,0.8588235,0.3098039,1;rgb;ccw:0.941406;244,220,78,255,rgb:0.9568627,0.8627451,0.3058824,1;rgb;ccw:0.945313;246,221,77,255,rgb:0.9647059,0.8666667,0.3019608,1;rgb;ccw:0.949219;247,222,76,255,rgb:0.9686275,0.8705882,0.2980392,1;rgb;ccw:0.953125;248,223,75,255,rgb:0.972549,0.8745098,0.2941176,1;rgb;ccw:0.957031;249,224,74,255,rgb:0.9764706,0.8784314,0.2901961,1;rgb;ccw:0.960938;250,225,73,255,rgb:0.9803922,0.8823529,0.2862745,1;rgb;ccw:0.964844;251,226,72,255,rgb:0.9843137,0.8862745,0.2823529,1;rgb;ccw:0.96875;253,227,70,255,rgb:0.9921569,0.8901961,0.2745098,1;rgb;ccw:0.972656;254,228,69,255,rgb:0.9960784,0.8941176,0.2705882,1;rgb;ccw:0.976563;255,229,68,255,rgb:1,0.8980392,0.2666667,1;rgb;ccw:0.980469;255,230,66,255,rgb:1,0.9019608,0.2588235,1;rgb;ccw:0.984375;255,231,66,255,rgb:1,0.9058824,0.2588235,1;rgb;ccw:0.988281;255,232,67,255,rgb:1,0.9098039,0.2627451,1;rgb;ccw"
REDS_STOPS_STRING = "0.0;255,245,240,255,rgb:1,0.9607843,0.9411765,1;rgb;ccw:0.13;254,224,210,255,rgb:0.9960784,0.8784314,0.8235294,1;rgb;ccw:0.26;252,187,161,255,rgb:0.9882353,0.7333333,0.6313725,1;rgb;ccw:0.39;252,146,114,255,rgb:0.9882353,0.572549,0.4470588,1;rgb;ccw:0.52;251,106,74,255,rgb:0.9843137,0.4156863,0.2901961,1;rgb;ccw:0.65;239,59,44,255,rgb:0.9372549,0.2313725,0.172549,1;rgb;ccw:0.78;203,24,29,255,rgb:0.7960784,0.0941176,0.1137255,1;rgb;ccw:0.9;165,15,21,255,rgb:0.6470588,0.0588235,0.0823529,1;rgb;ccw:1.0;103,0,13,255,rgb:0.4039216,0,0.0509804,1;rgb;ccw"
GRAYS_STOPS_STRING = "0.0;250,250,250,255,rgb:0.9803922,0.9803922,0.9803922,1;rgb;ccw:1.0;5,5,5,255,rgb:0.0196078,0.0196078,0.0196078,1;rgb;ccw"


# ------------------------------------------------------------------------------
# TopographicOpennessIndex – ArcGIS Pro–safe reimplementation
#
# This tool re‑implements the openness (OPNS) algorithm described in:
#   Relief Visualization Toolbox (RVT)
#   © 2010–2020 Research Centre of the Slovenian Academy of Sciences and Arts
#   © 2016–2020 University of Ljubljana, Faculty of Civil and Geodetic Engineering
#
# Original authors of RVT include:
#   Žiga Kokalj, Krištof Oštir, Klemen Zakšek, Peter Pehani,
#   Klemen Čotar, Maja Somrak, Žiga Maroh, Nejc Čož
#
# This ArcGIS Pro tool does NOT include RVT code.
# It is an independent implementation based on published algorithmic descriptions.
# ------------------------------------------------------------------------------

def _parse_qgis_stops_qml(stops_string):
    stops=[]
    if not stops_string:return stops
    for block in stops_string.split(":"):
        block=block.strip()
        if not block:continue
        parts=block.split(";")
        if len(parts)<2:continue
        try:pos=float(parts[0])
        except:continue
        rgb=parts[1].split(",")
        if len(rgb)<3:continue
        try:r=int(rgb[0]);g=int(rgb[1]);b=int(rgb[2])
        except:continue
        stops.append((pos,(r,g,b)))
    stops.sort(key=lambda x:x[0])
    return stops

def _build_lut_from_stops(stops,n=256):
    if not stops:return np.zeros((n,3),dtype=np.uint8)
    pos=np.array([s[0] for s in stops],dtype=np.float64)
    col=np.array([s[1] for s in stops],dtype=np.float64)
    xs=np.linspace(0.0,1.0,n)
    lut=np.zeros((n,3),dtype=np.uint8)
    for i in range(3):
        lut[:,i]=np.interp(xs,pos,col[:,i]).clip(0,255).astype(np.uint8)
    return lut

CIVIDIS_LUT=_build_lut_from_stops(_parse_qgis_stops_qml(CIVIDIS_STOPS_STRING),256)
REDS_LUT   =_build_lut_from_stops(_parse_qgis_stops_qml(REDS_STOPS_STRING),256)
GRAYS_LUT  =_build_lut_from_stops(_parse_qgis_stops_qml(GRAYS_STOPS_STRING),256)

# ----------------------------------------------------------------------
# HORIZON SCANNING + OPENNESS ENGINE
# ----------------------------------------------------------------------
@lru_cache(maxsize=16)
def _horizon_shift_vector_cached(ndirs,radius,min_radius=1):
    dirs=[]
    ang=(2*np.pi/ndirs)*np.arange(ndirs,dtype=np.float64)
    dx=np.cos(ang);dy=np.sin(ang)
    scale=3.0
    radii=np.arange((radius-min_radius)*scale+1,dtype=np.float64)/scale+min_radius
    for i in range(ndirs):
        xi=np.rint(dx[i]*radii).astype(np.int32)
        yi=np.rint(dy[i]*radii).astype(np.int32)
        pairs=np.unique(np.stack((yi,xi),axis=1),axis=0)
        dist=np.sqrt((pairs.astype(np.float64)**2).sum(axis=1))
        keep=dist>0
        pairs=pairs[keep];dist=dist[keep]
        o=np.argsort(dist)
        dirs.append((pairs[o].astype(np.int32),(1.0/dist[o]).astype(np.float32)))
    return tuple(dirs)

def _compute_openness_pos_neg_fast(dem_arr,radius,ndirs,out_nodata,in_nodata=None):
    dem=np.asarray(dem_arr,np.float32)
    h,w=dem.shape;pad=int(radius)
    invalid=~np.isfinite(dem)
    if in_nodata is not None:
        try:
            if np.isfinite(in_nodata):invalid|=(dem==np.float32(in_nodata))
        except:pass
    if invalid.any():
        dem=dem.copy();dem[invalid]=np.float32(out_nodata)
    dem_pad=np.pad(dem,pad,mode="reflect")
    center=dem_pad[pad:pad+h,pad:pad+w]
    dirs=_horizon_shift_vector_cached(int(ndirs),int(radius))
    pos_sum=np.zeros((h,w),np.float32)
    neg_sum=np.zeros((h,w),np.float32)
    max_pos=np.empty((h,w),np.float32)
    max_neg=np.empty((h,w),np.float32)
    work=np.empty((h,w),np.float32)
    for shifts,inv_dists in dirs:
        max_pos.fill(-1000.0);max_neg.fill(-1000.0)
        for k in range(shifts.shape[0]):
            dy,dx=shifts[k];inv=inv_dists[k]
            y0=pad-dy;x0=pad-dx
            y1=y0+h;x1=x0+w
            nb=dem_pad[y0:y1,x0:x1]
            np.subtract(nb,center,out=work)
            np.multiply(work,inv,out=work)
            np.maximum(max_pos,work,out=max_pos)
            np.negative(work,out=work)
            np.maximum(max_neg,work,out=max_neg)
        np.arctan(max_pos,out=max_pos)
        np.arctan(max_neg,out=max_neg)
        pos_sum+=max_pos;neg_sum+=max_neg
    scale=np.float32(1.0/ndirs);half_pi=np.float32(0.5*np.pi)
    pos_sum=(half_pi-pos_sum*scale)
    neg_sum=(half_pi-neg_sum*scale)
    np.degrees(pos_sum,out=pos_sum)
    np.degrees(neg_sum,out=neg_sum)
    if invalid.any():
        pos_sum[invalid]=np.float32(out_nodata)
        neg_sum[invalid]=np.float32(out_nodata)
    return pos_sum,neg_sum

class TopographicOpennessIndex(object):
    def __init__(self):
        self.label="1. Topographic Openness Index (POS–NEG)"
        self.description="Computes openness index from DEM: (POS-NEG)/2, writes <basename>_open.tif (GTiff)."
        self.canRunInBackground=False

    def getParameterInfo(self):
        p_r=arcpy.Parameter(displayName="Input DEM(s)",name="in_rasters",datatype="GPRasterLayer",parameterType="Optional",direction="Input",multiValue=True)
        p_f=arcpy.Parameter(displayName="Input Folder (optional)",name="in_folder",datatype="DEFolder",parameterType="Optional",direction="Input")
        p_rad=arcpy.Parameter(displayName="Search Radius (pixels)",name="radius",datatype="GPLong",parameterType="Required",direction="Input");p_rad.value=100
        p_ndr=arcpy.Parameter(displayName="Number of Directions",name="ndirs",datatype="GPLong",parameterType="Required",direction="Input")
        p_ndr.filter.type="ValueList";p_ndr.filter.list=["8","16"];p_ndr.value="8"
        p_out=arcpy.Parameter(displayName="Output Folder",name="out_folder",datatype="DEWorkspace",parameterType="Required",direction="Output")
        p_nd=arcpy.Parameter(displayName="Output NoData value",name="out_nodata",datatype="GPDouble",parameterType="Optional",direction="Input");p_nd.value=-9999.0
        p_dbg=arcpy.Parameter(displayName="Debug Mode",name="debug_mode",datatype="GPBoolean",parameterType="Optional",direction="Input");p_dbg.value=False
        return[p_r,p_f,p_rad,p_ndr,p_out,p_nd,p_dbg]

    def _add(self,r):
        try:
            m=arcpy.mp.ArcGISProject("CURRENT").activeMap
            m.addDataFromPath(r)
        except:pass

    def _write_tif(self,out_path,data,ref_ds,nodata):
        driver=gdal.GetDriverByName("GTiff")
        opts=["COMPRESS=DEFLATE","PREDICTOR=2","TILED=YES"]
        rows=ref_ds.RasterYSize;cols=ref_ds.RasterXSize
        gt=ref_ds.GetGeoTransform();prj=ref_ds.GetProjection()
        ds=driver.Create(out_path,cols,rows,1,gdal.GDT_Float32,options=opts)
        if ds is None:raise RuntimeError(f"Could not create {out_path}")
        ds.SetGeoTransform(gt);ds.SetProjection(prj)
        b=ds.GetRasterBand(1);b.WriteArray(data);b.SetNoDataValue(nodata);b.FlushCache()
        ds.FlushCache();ds=None

    def execute(self,p,msg):
        ras=p[0].values
        folder=p[1].valueAsText
        radius=int(p[2].value)
        ndirs=int(p[3].value)
        out=p[4].valueAsText
        nodata=float(p[5].value)
        dbg=bool(p[6].value)
        if not os.path.exists(out):os.makedirs(out)
        def log(t):msg.addMessage(t)
        dem_list=[]
        if ras:dem_list.extend(list(ras))
        if folder:
            for f in os.listdir(folder):
                if f.lower().endswith((".tif",".tiff",".img")):dem_list.append(os.path.join(folder,f))
        if not dem_list:raise arcpy.ExecuteError("No DEMs found.")
        log(f"Processing {len(dem_list)} DEM(s)...")
        log(f"Radius {radius} | Directions {ndirs}")
        log("Output: <basename>_open.tif (GTiff)")
        outputs=[]
        def process(dem_input):
            try:
                try:dem_path=arcpy.Describe(dem_input).catalogPath
                except:dem_path=str(dem_input)
                base=os.path.splitext(os.path.basename(dem_path))[0]
                out_path=os.path.join(out,f"{base}_open.tif")
                t0=time.perf_counter()
                ds=gdal.Open(dem_path)
                if ds is None:raise RuntimeError(f"Could not open {dem_path}")
                band=ds.GetRasterBand(1)
                in_nd=band.GetNoDataValue()
                arr=band.ReadAsArray().astype(np.float32,copy=False)
                t_read=time.perf_counter()
                pos,neg=_compute_openness_pos_neg_fast(arr,radius,ndirs,nodata,in_nodata=in_nd)
                t_compute=time.perf_counter()
                mask=np.zeros_like(pos,bool)
                mask|=(pos==nodata)
                mask|=(neg==nodata)
                pos_valid=np.where(~mask,pos,np.nan)
                neg_valid=np.where(~mask,neg,np.nan)
                out_arr=(pos_valid-neg_valid)/2.0
                out_arr[~np.isfinite(out_arr)]=nodata
                t_index=time.perf_counter()
                self._write_tif(out_path,out_arr,ds,nodata)
                ds=None
                t_write=time.perf_counter()
                outputs.append(out_path)
                if dbg:return(f"{base}: read {t_read-t0:.2f}s, compute {t_compute-t_read:.2f}s, index {t_index-t_compute:.2f}s, write {t_write-t_index:.2f}s, total {t_write-t0:.2f}s")
                return(f"{base}: total {t_write-t0:.2f}s")
            except Exception as e:
                return f"{dem_input}: ERROR {e}"
        workers=min(8,len(dem_list))
        log(f"Using {workers} worker(s), capped at 8 for stable production throughput.")
        with ThreadPoolExecutor(max_workers=workers) as ex:
            for fut in as_completed([ex.submit(process,d) for d in dem_list]):
                log(fut.result())
        if not folder:
            for r in outputs:self._add(r)
        log("All DEMs processed.")


class SlopeFromDEM(object):
    def __init__(self):
        self.label="2. Slope from DEM"
        self.description="Computes Horn slope"
        self.canRunInBackground=False

    def getParameterInfo(self):
        p_dem=arcpy.Parameter(displayName="Input DEM",name="in_dem",datatype="GPRasterLayer",parameterType="Optional",direction="Input")
        p_folder=arcpy.Parameter(displayName="Input Folder (optional, DEM tiles)",name="in_folder",datatype="DEFolder",parameterType="Optional",direction="Input")
        p_out=arcpy.Parameter(displayName="Output Folder",name="out_folder",datatype="DEFolder",parameterType="Required",direction="Output")
        p_nd=arcpy.Parameter(displayName="Output NoData value",name="out_nodata",datatype="GPDouble",parameterType="Optional",direction="Input")
        p_nd.value=-9999.0
        return[p_dem,p_folder,p_out,p_nd]

    def _compute_slope(self,arr,gt):
        xres=gt[1];yres=abs(gt[5])
        dem=arr.astype(np.float32,copy=False)
        a=dem[:-2,:-2];b=dem[:-2,1:-1];c=dem[:-2,2:]
        d=dem[1:-1,:-2];f=dem[1:-1,2:]
        g=dem[2:,:-2];h=dem[2:,1:-1];i=dem[2:,2:]
        dzdx=((c+2*f+i)-(a+2*d+g))/(8*xres)
        dzdy=((g+2*h+i)-(a+2*b+c))/(8*yres)
        core=np.degrees(np.arctan(np.sqrt(dzdx*dzdx+dzdy*dzdy))).astype(np.float32,copy=False)
        slope=np.zeros_like(dem,np.float32)
        slope[1:-1,1:-1]=core
        return slope

    def _write_tif(self,out_path,data,ref_ds,out_nodata):
        driver=gdal.GetDriverByName("GTiff")
        opts=["TILED=YES","BIGTIFF=IF_SAFER","STATISTICS=NO","COLORINTERP=undefined","COPY_SRC_OVERVIEWS=NO"]
        rows=ref_ds.RasterYSize;cols=ref_ds.RasterXSize
        gt=ref_ds.GetGeoTransform();prj=ref_ds.GetProjection()
        ds=driver.Create(out_path,cols,rows,1,gdal.GDT_Float32,opts)
        ds.SetGeoTransform(gt);ds.SetProjection(prj)
        b=ds.GetRasterBand(1)
        b.WriteArray(data)
        b.FlushCache()
        ds.FlushCache();ds=None

    def _add(self,r):
        try:
            m=arcpy.mp.ArcGISProject("CURRENT").activeMap
            m.addDataFromPath(r)
        except:pass

    def execute(self,p,msg):
        dem=p[0].value
        folder=p[1].valueAsText
        out=p[2].valueAsText
        out_nodata=float(p[3].value)
        if not os.path.exists(out):os.makedirs(out)
        def process(path):
            base=os.path.splitext(os.path.basename(path))[0]
            out_path=os.path.join(out,f"{base}_slope.tif")
            msg.addMessage(f"Computing slope: {base}")
            ds=gdal.Open(path)
            band=ds.GetRasterBand(1)
            arr=band.ReadAsArray()
            slope=self._compute_slope(arr,ds.GetGeoTransform())
            self._write_tif(out_path,slope,ds,out_nodata)
            ds=None
            if not folder:self._add(out_path)
        if folder:
            for f in os.listdir(folder):
                if f.lower().endswith((".tif",".tiff",".img")):
                    process(os.path.join(folder,f))
            return
        if not dem:raise arcpy.ExecuteError("Provide DEM or folder.")
        process(arcpy.Describe(dem).catalogPath)


class RedReliefImageMap(object):
    def __init__(self):
        self.label="3. Red Relief Image Map (RRIM)"
        self.description="RRIM: Cividis openness + red-tinted slope overlay (true RGB)."
        self.canRunInBackground=False

    def getParameterInfo(self):
        p1=arcpy.Parameter(displayName="Slope Raster (single-tile mode)",name="in_slope",datatype="GPRasterLayer",parameterType="Optional",direction="Input")
        p2=arcpy.Parameter(displayName="Openness Raster (single-tile mode)",name="in_open",datatype="GPRasterLayer",parameterType="Optional",direction="Input")
        p3=arcpy.Parameter(displayName="Slope Folder (optional, batch mode)",name="slope_folder",datatype="DEFolder",parameterType="Optional",direction="Input")
        p4=arcpy.Parameter(displayName="Openness Folder (optional, batch mode)",name="open_folder",datatype="DEFolder",parameterType="Optional",direction="Input")
        p5=arcpy.Parameter(displayName="Output Folder",name="out_folder",datatype="DEFolder",parameterType="Required",direction="Output")
        p6=arcpy.Parameter(displayName="Output NoData value (RGB)",name="out_nodata",datatype="GPLong",parameterType="Optional",direction="Input");p6.value=-9999
        return[p1,p2,p3,p4,p5,p6]

    def _compute_rrim_core(self,slope_path,open_path):
        s_ds=gdal.Open(slope_path);o_ds=gdal.Open(open_path)
        s=s_ds.GetRasterBand(1).ReadAsArray().astype(np.float32)
        o=o_ds.GetRasterBand(1).ReadAsArray().astype(np.float32)
        sn=s_ds.GetRasterBand(1).GetNoDataValue();on=o_ds.GetRasterBand(1).GetNoDataValue()
        m=np.zeros_like(s,bool)
        if sn is not None:m|=(s==sn)
        if on is not None:m|=(o==on)
        s=np.where(~m,s,np.nan);o=np.where(~m,o,np.nan)
        ov=o[np.isfinite(o)];sv=s[np.isfinite(s)]
        omin=float(ov.mean()-3.5*ov.std());omax=float(ov.mean()+3.5*ov.std())
        smin=max(0.0,float(sv.mean()-4*sv.std()));smax=float(sv.mean()+4*sv.std())
        onorm=np.clip((o-omin)/(omax-omin),0,1);snorm=np.clip((s-smin)/(smax-smin),0,1)
        onorm[~np.isfinite(onorm)]=0;snorm[~np.isfinite(snorm)]=0
        oi=(onorm*255).astype(np.uint8);si=(snorm*255).astype(np.uint8)
        c=CIVIDIS_LUT[oi];r=REDS_LUT[si]
        try:b=_blend_rgb(c.astype(np.float32),r.astype(np.float32),0.7).astype(np.uint8)
        except:b=((1-0.7)*c+0.7*r).clip(0,255).astype(np.uint8)
        return b[:,:,0],b[:,:,1],b[:,:,2],s_ds

    def _save_tif(self,R,G,B,src_ds,out_path,nd):
        gt=src_ds.GetGeoTransform();prj=src_ds.GetProjection()
        driver=gdal.GetDriverByName("GTiff")
        opts=["COMPRESS=DEFLATE","PREDICTOR=2","TILED=YES","BIGTIFF=IF_SAFER"]
        ds=driver.Create(out_path,src_ds.RasterXSize,src_ds.RasterYSize,3,gdal.GDT_Byte,opts)
        ds.SetGeoTransform(gt);ds.SetProjection(prj)
        ds.GetRasterBand(1).WriteArray(R);ds.GetRasterBand(1).SetNoDataValue(nd)
        ds.GetRasterBand(2).WriteArray(G);ds.GetRasterBand(2).SetNoDataValue(nd)
        ds.GetRasterBand(3).WriteArray(B);ds.GetRasterBand(3).SetNoDataValue(nd)
        ds.FlushCache();ds=None
        aux=out_path+".aux.xml"
        try:
            with open(aux,"w",encoding="utf-8") as f:
                f.write("<PAMDataset>\n  <Metadata>\n    <MDI key=\"DataType\">Processed</MDI>\n  </Metadata>\n</PAMDataset>\n")
        except:pass

    def _add_rgb(self,tif):
        try:
            tif=os.path.abspath(tif)
            aprx=arcpy.mp.ArcGISProject("CURRENT");m=aprx.activeMap
            lyr=m.addDataFromPath(tif)
            sym=lyr.symbology
            sym.updateColorizer("RasterRGBColorizer")
            cz=sym.colorizer
            if hasattr(cz,"redBand"):cz.redBand="Band_1"
            if hasattr(cz,"greenBand"):cz.greenBand="Band_2"
            if hasattr(cz,"blueBand"):cz.blueBand="Band_3"
            if hasattr(cz,"stretchType"):cz.stretchType="None"
            lyr.symbology=sym
        except:pass

    def _process_one(self,slope_path,open_path,out_folder,nd,msg,suffix,single):
        R,G,B,src_ds=self._compute_rrim_core(slope_path,open_path)
        base=os.path.splitext(os.path.basename(slope_path))[0]
        if base.lower().endswith("_slope"):base=base[:-6]
        tif=os.path.join(out_folder,f"{base}_{suffix}.tif")
        msg.addMessage(f"Saving TIFF: {tif}")
        self._save_tif(R,G,B,src_ds,tif,nd)
        if single:self._add_rgb(tif)

    def execute(self,p,msg):
        arcpy.env.addOutputsToMap=False
        s=p[0].value;o=p[1].value
        sf=p[2].valueAsText;of=p[3].valueAsText
        out=p[4].valueAsText;nd=p[5].value
        if not os.path.exists(out):os.makedirs(out)
        if sf and of:
            sl=[f for f in os.listdir(sf) if f.lower().endswith((".tif",".img"))]
            ol=[f for f in os.listdir(of) if f.lower().endswith((".tif",".img"))]
            sd={};od={}
            for f in sl:
                if "_slope" in f.lower():sd[os.path.splitext(f.lower().replace("_slope",""))[0]]=os.path.join(sf,f)
            for f in ol:
                if "_open" in f.lower():od[os.path.splitext(f.lower().replace("_open",""))[0]]=os.path.join(of,f)
            for k in sorted(set(sd)&set(od)):
                msg.addMessage(f"Computing RRIM for {k}")
                self._process_one(sd[k],od[k],out,nd,msg,"rrim",False)
            return
        sp=arcpy.Describe(s).catalogPath
        op=arcpy.Describe(o).catalogPath
        msg.addMessage("Computing RRIM (single-tile mode)")
        self._process_one(sp,op,out,nd,msg,"rrim",True)


class RedReliefImageMapClassic(object):
    def __init__(self):
        self.label="4. Red Relief Image Map (Classic)"
        self.description="Classic RRIM: grayscale openness + red-tinted slope overlay."
        self.canRunInBackground=False

    def getParameterInfo(self):
        p1=arcpy.Parameter(displayName="Slope Raster (single-tile mode)",name="in_slope",datatype="GPRasterLayer",parameterType="Optional",direction="Input")
        p2=arcpy.Parameter(displayName="Openness Raster (single-tile mode)",name="in_open",datatype="GPRasterLayer",parameterType="Optional",direction="Input")
        p3=arcpy.Parameter(displayName="Slope Folder (optional, batch mode)",name="slope_folder",datatype="DEFolder",parameterType="Optional",direction="Input")
        p4=arcpy.Parameter(displayName="Openness Folder (optional, batch mode)",name="open_folder",datatype="DEFolder",parameterType="Optional",direction="Input")
        p5=arcpy.Parameter(displayName="Output Folder",name="out_folder",datatype="DEFolder",parameterType="Required",direction="Output")
        p6=arcpy.Parameter(displayName="Output NoData value (RGB)",name="out_nodata",datatype="GPLong",parameterType="Optional",direction="Input");p6.value=-9999
        return[p1,p2,p3,p4,p5,p6]

    def _compute_rrim_classic_core(self,slope_path,open_path):
        s_ds=gdal.Open(slope_path);o_ds=gdal.Open(open_path)
        s=s_ds.GetRasterBand(1).ReadAsArray().astype(np.float32)
        o=o_ds.GetRasterBand(1).ReadAsArray().astype(np.float32)
        sn=s_ds.GetRasterBand(1).GetNoDataValue();on=o_ds.GetRasterBand(1).GetNoDataValue()
        m=np.zeros_like(s,bool)
        if sn is not None:m|=(s==sn)
        if on is not None:m|=(o==on)
        s=np.where(~m,s,np.nan);o=np.where(~m,o,np.nan)
        sv=s[np.isfinite(s)];ov=o[np.isfinite(o)]
        smin=float(np.percentile(sv,0.5));smax=float(np.percentile(sv,99.5))
        omin=float(np.percentile(ov,0.5));omax=float(np.percentile(ov,99.5))
        snorm=np.clip((s-smin)/(smax-smin+1e-6),0,1)
        onorm=np.clip((o-omin)/(omax-omin+1e-6),0,1)
        snorm[~np.isfinite(snorm)]=0;onorm[~np.isfinite(onorm)]=0
        si=(snorm*255).astype(np.uint8);oi=(onorm*255).astype(np.uint8)
        g=GRAYS_LUT[255-oi];r=REDS_LUT[si]
        try:b=_blend_rgb(g.astype(np.float32),r.astype(np.float32),0.7).astype(np.uint8)
        except:b=((1-0.7)*g+0.7*r).clip(0,255).astype(np.uint8)
        return b[:,:,0],b[:,:,1],b[:,:,2],s_ds

    def _save_tif(self,R,G,B,src_ds,out_path,nd):
        gt=src_ds.GetGeoTransform();prj=src_ds.GetProjection()
        driver=gdal.GetDriverByName("GTiff")
        opts=["COMPRESS=DEFLATE","PREDICTOR=2","TILED=YES","BIGTIFF=IF_SAFER"]
        ds=driver.Create(out_path,src_ds.RasterXSize,src_ds.RasterYSize,3,gdal.GDT_Byte,opts)
        ds.SetGeoTransform(gt);ds.SetProjection(prj)
        ds.GetRasterBand(1).WriteArray(R);ds.GetRasterBand(1).SetNoDataValue(nd)
        ds.GetRasterBand(2).WriteArray(G);ds.GetRasterBand(2).SetNoDataValue(nd)
        ds.GetRasterBand(3).WriteArray(B);ds.GetRasterBand(3).SetNoDataValue(nd)
        ds.FlushCache();ds=None
        aux=out_path+".aux.xml"
        try:
            with open(aux,"w",encoding="utf-8") as f:
                f.write("<PAMDataset>\n  <Metadata>\n    <MDI key=\"DataType\">Processed</MDI>\n  </Metadata>\n</PAMDataset>\n")
        except:pass

    def _add_rgb(self,tif):
        try:
            tif=os.path.abspath(tif)
            aprx=arcpy.mp.ArcGISProject("CURRENT");m=aprx.activeMap
            lyr=m.addDataFromPath(tif)
            sym=lyr.symbology
            sym.updateColorizer("RasterRGBColorizer")
            cz=sym.colorizer
            if hasattr(cz,"redBand"):cz.redBand="Band_1"
            if hasattr(cz,"greenBand"):cz.greenBand="Band_2"
            if hasattr(cz,"blueBand"):cz.blueBand="Band_3"
            if hasattr(cz,"stretchType"):cz.stretchType="None"
            lyr.symbology=sym
        except:pass

    def _process_one(self,slope_path,open_path,out_folder,nd,msg,suffix,single):
        R,G,B,src_ds=self._compute_rrim_classic_core(slope_path,open_path)
        base=os.path.splitext(os.path.basename(slope_path))[0]
        if base.lower().endswith("_slope"):base=base[:-6]
        tif=os.path.join(out_folder,f"{base}_{suffix}.tif")
        msg.addMessage(f"Saving TIFF: {tif}")
        self._save_tif(R,G,B,src_ds,tif,nd)
        if single:self._add_rgb(tif)

    def execute(self,p,msg):
        arcpy.env.addOutputsToMap=False
        s=p[0].value;o=p[1].value
        sf=p[2].valueAsText;of=p[3].valueAsText
        out=p[4].valueAsText;nd=p[5].value
        if not os.path.exists(out):os.makedirs(out)
        if sf and of:
            sl=[f for f in os.listdir(sf) if f.lower().endswith((".tif",".img"))]
            ol=[f for f in os.listdir(of) if f.lower().endswith((".tif",".img"))]
            sd={};od={}
            for f in sl:
                if "_slope" in f.lower():sd[os.path.splitext(f.lower().replace("_slope",""))[0]]=os.path.join(sf,f)
            for f in ol:
                if "_open" in f.lower():od[os.path.splitext(f.lower().replace("_open",""))[0]]=os.path.join(of,f)
            for k in sorted(set(sd)&set(od)):
                msg.addMessage(f"Computing Classic RRIM for {k}")
                self._process_one(sd[k],od[k],out,nd,msg,"rrim_classic",False)
            return
        sp=arcpy.Describe(s).catalogPath
        op=arcpy.Describe(o).catalogPath
        msg.addMessage("Computing Classic RRIM (single-tile mode)")
        self._process_one(sp,op,out,nd,msg,"rrim_classic",True)