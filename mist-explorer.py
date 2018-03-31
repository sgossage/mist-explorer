'''
Interactively plots MIST style isochrones. Requires 
a modded version of Jieun Choi's MIST_codes, acquired 
here: https://github.com/sgossage/MIST_codes

Also requires a set of MIST/MESA models, which are not 
publicly available yet (but will be).

Use the ``bokeh serve`` command to run by executing:
    bokeh serve mist-explorer.py
at your command prompt. Then navigate to the URL
    http://localhost:5006/mist-explorer
in your browser.

To do:

 -- Speed this up. Takes 1.5 min to load the isochrones in (down from 5!).
 -- Consider best way to designate a reference isochrone. Save snapshots w/ labels?
    Or just do what it is nowish, and have seperate sliders to set the reference(s)?
 -- Make a version for evolutionary tracks?
 -- Add slider for grav. dark i and distance modulus (also Av? might be slow, have to call iso code).
 -- Add ability to load data?
 -- Ability to select phase via buttons.

'''
import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, TextInput, Select, RadioButtonGroup, Div, Panel, Tabs, RangeSlider
from bokeh.plotting import figure

from MIST_codes.scripts import read_mist_models as rmm
from tqdm import tqdm
import sys
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-ps", "--photset",
                    help="specify a desired photometry set for isochrones, e.g. UBVRIplus.")
parser.add_argument("-pf", "--photfile",
                    help="specify a desired photometric data file (format is just two magnitude columns, e.g.: V, I).")
args = parser.parse_args()
if args.photset:
    photstr = args.photset
else:
    photstr = 'UBVRIplus'
if args.photfile:
    photfn = args.photfile
    photd = np.genfromtxt(photfn)
    photv = photd.T[0]
    photi = photd.T[1]
    # data is plotted as v-i, i.
    phot_source = ColumnDataSource(data=dict(x=photv-photi, y=photi)) 
# check for input data file:
# (should be a file, two columns: blue filter, red filter magnitudes)
#if len(sys.argv) > 1:
    #photfn = sys.argv[1]
    #photd = np.genfromtxt(photfn)
    #photv = photd.T[0]
    #photi = photd.T[1]
    #phot_source = ColumnDataSource(data=dict(x=photv-photi, y=photi))
#    try:
#        photstr = sys.argv[1]
#    except IndexError:
#        photstr = 'UBVRIplus'
#else:
#    photstr = 'UBVRIplus'
        
# just grab one of the relevant bc_tables to get some default labels...
bc_table = os.path.join(os.environ['COLORS_DATA_DIR'], 'fehp000.{:s}'.format(photstr))
with open(bc_table, 'r') as bctab:
    lines = bctab.readlines()

bchdr = lines[5].split() 

v_label = bchdr[7] 
i_label = bchdr[8]
x_label = '{:s}-{:s}'.format(v_label, i_label)
y_label = '{:s}'.format(i_label)
# load isochrones so data access is faster
# storing in a dictionary d[feh][vvc][gd_i] to access:
feh_range = np.array([-0.30, -0.15, 0.00, 0.15, 0.30])
vvc_range = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
gdi_range = np.array([0.0, 45.0, 90.0])
mi_range = [round(x, 2) for x in np.linspace(0.1, 8.0, int((8-0.1)/0.5))]
isocmds = {}

# default CMD filters:
#x_label = 'Tycho_B-Tycho_V'
#y_label = 'Tycho_V'

for feh_val in tqdm(feh_range):
    # populate with isochrones at v/vc = 0.0...0.6 for each feh:
    i = {}
    for vvc_val in vvc_range:
        # populate with isochrones at gd_i = 0.0...0.90 for each v/vc:
        j = {}
        for gdi_val in gdi_range:
            j[gdi_val] = rmm.ISOCMD(feh=feh_val, vvcrit=vvc_val, gravdark_i=gdi_val, exttag='TP', photstr=photstr)
            # log10 age  = 8.5 is used as the default age.
            j[gdi_val].set_isodata(8.5, x_label, y_label, dmod=0.0)
        i[vvc_val] = j
            
    isocmds[feh_val] = i

# Use feh = 0.00, v/vc = 0.0, i=0.0 as default isochrone
x = isocmds[0.00][0.0][0.0].x
y = isocmds[0.00][0.0][0.0].y

x_hrd, y_hrd = (isocmds[0.00][0.0][0.0].get_data(['log_Teff', 'log_L'], [],
                                            lage = 8.5, dmod=0.0)).values()

# A reference CMD to compare to (feh = 0.0, v/vc = 0.0, i = 0.0,  age = 8.0):
x_ref, y_ref = (isocmds[0.00][0.0][0.0].get_data([x_label, y_label], [],
                                            lage = 8.0, dmod=0.0)).values()

x_ref_hrd, y_ref_hrd = (isocmds[0.00][0.0][0.0].get_data(['log_Teff', 'log_L'], [],
                                            lage = 8.0, dmod=0.0)).values()

# An underlying isohrone to display mass range:
x_mi, y_mi = (isocmds[0.00][0.0][0.0].get_data([x_label, y_label], [],
                                               lage = 8.5, dmod=0.0, mrange=[0.1,8.0])).values()

x_mi_hrd, y_mi_hrd = (isocmds[0.00][0.0][0.0].get_data(['log_Teff', 'log_L'], [],
                                               lage = 8.5, dmod=0.0, mrange=[0.1,8.0])).values()


# data source for main iso and reference:
source = ColumnDataSource(data=dict(x=x, y=y))
source_ref = ColumnDataSource(data=dict(x=x_ref, y=y_ref))
source_mi = ColumnDataSource(data=dict(x=x_mi, y=y_mi))

source_hrd = ColumnDataSource(data=dict(x=x_hrd, y=y_hrd))
source_ref_hrd = ColumnDataSource(data=dict(x=x_ref_hrd, y=y_ref_hrd))
source_mi_hrd = ColumnDataSource(data=dict(x=x_mi_hrd, y=y_mi_hrd))

# Set up plots...
# CMD
# Figure:
plot_CMD = figure(plot_height=800, plot_width=600,
                  tools="box_zoom,crosshair,pan,reset,save,wheel_zoom",
              x_range=[x.min(), x.max()], y_range=[y.max(), y.min()])

# Draw CMD lines
plot_CMD.line('x', 'y', source=source, line_width=1, line_alpha=0.6)
plot_CMD.line('x', 'y', source=source_ref, line_width=1, line_alpha=0.6,
          line_color='black', line_dash="4 4")
plot_CMD.line('x', 'y', source=source_mi, line_width=3, line_alpha=0.2, 
              line_color='red')

# place data on CMD if provided:
if args.photfile:
    plot_CMD.scatter('x', 'y', source=phot_source, alpha=0.6)


# CMD tab:
cmdtab = Panel(child=plot_CMD, title="CMD")

# HRD:
# Figure:
plot_HRD = figure(plot_height=800, plot_width=600,
              tools="crosshair,pan,reset,save,wheel_zoom",
              x_range=[x_hrd.max(), x_hrd.min()], y_range=[y_hrd.min(), y_hrd.max()])

# Draw HRD lines:
plot_HRD.line('x', 'y', source=source_hrd, line_width=1, line_alpha=0.6)
plot_HRD.line('x', 'y', source=source_ref_hrd, line_width=1, line_alpha=0.6,
          line_color='black', line_dash="4 4")
plot_HRD.line('x', 'y', source=source_mi_hrd, line_width=3, line_alpha=0.2, 
              line_color='red')

# HRD tab:
hrdtab = Panel(child=plot_HRD, title="HRD")

# x, y axis labels:
plot_CMD.xaxis.axis_label = x_label
plot_CMD.yaxis.axis_label = y_label
plot_HRD.xaxis.axis_label = 'log_Teff'
plot_HRD.yaxis.axis_label = 'log_L'

# Set up widgets...
# for data:
lage = Slider(title="log(age)", value=8.5, start=7.5, end=10.0, step=0.02)
vvc = Slider(title=r"V/Vc", value=0.0, start=0.0, end=0.6, step=0.1)
feh = Slider(title="[Fe/H]", value=0.0, start=-0.30, end=0.30, step=0.15)
gdi = Slider(title="i [deg]", value=0.0, start=0.0, end=90.0, step=45.0)
dmod = Slider(title="Distance modulus [mag]", value=0.0, start=-99.0, end=99.0, step=0.1)

lage_ref = Slider(title="log(age) (reference)", value=8.0, start=7.5, end=10.0, step=0.02)
vvc_ref = Slider(title=r"V/Vc (reference)", value=0.0, start=0.0, end=0.6, step=0.1)
feh_ref = Slider(title="[Fe/H] (reference)", value=0.0, start=-0.30, end=0.30, step=0.15)
gdi_ref = Slider(title="i [deg] (reference)", value=0.0, start=0.0, end=90.0, step=45.0)
dmod_ref = Slider(title="Distance modulus [mag] (reference)", value=0.0, start=-99.0, end=99.0, step=0.1)

# for labels (filters):
lbl_ops = ['None', '-', '+', '*', '/']
filters_optional = ['None']
filters = []
for afilter in isocmds[0.00][0.0][0.0].hdr_list[9:-1]:
    filters.append(afilter)
    filters_optional.append(afilter)

# axis value and operator selection
# x-axis:
x_lbl1 = Select(title="x-axis value 1", value=v_label, options = filters)
x_op_title = Div(text="""x-axis operator (optional)""", height=10, width=200)
x_op = RadioButtonGroup(active=1, labels = lbl_ops)
x_lbl2 = Select(title="x-axis value 2 (optional)", value=i_label, options = filters_optional)
#y-axis:
y_lbl1 = Select(title="y-axis value 1", value=i_label, options = filters)
y_op_title = Div(text="""y-axis operator (optional)""", height=10, width=200)
y_op = RadioButtonGroup(active=0, labels = lbl_ops)
y_lbl2 = Select(title="y-axis value 2 (optional)", value='None', options = filters_optional)

# initial mass slider:
mi_slider = RangeSlider(start=mi_range[0], end=mi_range[-1], 
                        value=(0.1, 8.0), step=0.1, 
                        title="Initial Mass")

# Figure panel tabs:
tabs = Tabs(tabs=[cmdtab, hrdtab])

# Set up callbacks
def construct_lbl(s1, op, s2):
    """Builds a string according to style 
       of axis labels in this code. Given 
       first piece, an operator, and a second 
       piece, build 1st+op+2nd."""

    # always start with e.g. x_lbl1:
    lbl = s1
    # if there's an operator selected and secondary filter, use them:
    if op != 'None' and s2 != 'None':
        lbl += op+s2
    # if no operator selected, force sole usage of first filter:
    if op == 'None':
        lbl = s1
        
    return lbl

def update_data(attrname, old, new):

    # Get the current slider values
    la = float("{:.2f}".format(lage.value))
    v = float("{:.1f}".format(vvc.value))
    m = float("{:.2f}".format(feh.value))    
    i = float("{:.1f}".format(gdi.value))
    mu = float("{:.2f}".format(dmod.value))
    
    lar = float("{:.2f}".format(lage_ref.value))
    vr = float("{:.1f}".format(vvc_ref.value))
    mr = float("{:.2f}".format(feh_ref.value))    
    ir = float("{:.1f}".format(gdi_ref.value))
    mur = float("{:.2f}".format(dmod_ref.value))

    # Get current label selections:
    x1 = x_lbl1.value
    xop = lbl_ops[x_op.active]#value
    x2 = x_lbl2.value

    # construct the new label:
    x_label = construct_lbl(x1, xop, x2)

    # do the same for y-axis:
    y1 = y_lbl1.value
    yop = lbl_ops[y_op.active]
    y2 = y_lbl2.value
    y_label = construct_lbl(y1, yop, y2)

    # get current range for initial mass slider:
    mis, mie = mi_slider.value
    
    # update CMD data:
    df = isocmds[m][v][i].get_data([x_label, y_label], [], lage = la, dmod=mu)
    df_ref = isocmds[mr][vr][ir].get_data([x_label, y_label], [], lage = lar, dmod=mu)
    mi_cmd = isocmds[m][v][i].get_data([x_label, y_label], [], lage = la, dmod=mu,mrange=[mis,mie])

    # update HRD data:
    df_hrd = isocmds[m][v][i].get_data(['log_Teff', 'log_L'], [], lage = la, dmod=mur)
    df_ref_hrd = isocmds[mr][vr][ir].get_data(['log_Teff', 'log_L'], [], lage = lar, dmod=mur)
    mi_hrd = isocmds[m][v][i].get_data(['log_Teff', 'log_L'], [], lage = la, dmod=mur,mrange=[mis,mie])
    
    # Generate the new curve...
    # assign new data values...
    x, y = df.values()
    xr,yr = df_ref.values()
    xmicmd,ymicmd = mi_cmd.values()
    xhrd, yhrd = df_hrd.values()
    xrhrd,yrhrd = df_ref_hrd.values()
    xmihrd,ymihrd = mi_hrd.values()
    
    # re-assign source data...
    source.data = dict(x=x, y=y)
    source_ref.data = dict(x=xr, y=yr)
    source_mi.data = dict(x=xmicmd, y=ymicmd)

    source_hrd.data = dict(x=xhrd, y=yhrd)
    source_ref_hrd.data = dict(x=xrhrd, y=yrhrd)
    source_mi_hrd.data = dict(x=xmihrd, y=ymihrd)

    # update axes labels:
    plot_CMD.xaxis.axis_label = x_label
    plot_CMD.yaxis.axis_label = y_label

# update values on change via widgets:
for w in [lage, vvc, feh, gdi, dmod, lage_ref, vvc_ref, feh_ref,
          gdi_ref, dmod_ref, x_lbl1, x_lbl2, y_lbl1, y_lbl2]:
    
    w.on_change('value', update_data)

# update operator choices:
x_op.on_change('active', update_data)
y_op.on_change('active', update_data)

# update initial mass range:
mi_slider.on_change('value', update_data)

# Set up layouts and add to document
inputs = widgetbox(lage, vvc, feh, gdi, dmod, lage_ref, vvc_ref, feh_ref, gdi_ref, dmod_ref,
                   x_lbl1, x_op_title, x_op, x_lbl2, y_lbl1, y_op_title, y_op, 
                   y_lbl2, mi_slider)

curdoc().add_root(row(inputs, tabs, width=800))
curdoc().title = "Isochrone Explorer"
