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
 -- Following last point, best way to differentiate the isochrones?
 -- Make a version for evolutionary tracks?
 -- Make filters selectable. Maybe allow choice of y/x-axis.
 -- Add slider for grav. dark i and distance modulus (also Av? might be slow, have to call iso code).
 -- Add ability to load data?
 -- Ability to select phase via buttons.

'''
import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, TextInput, Select, RadioButtonGroup, Div
from bokeh.plotting import figure

from MIST_codes.scripts import read_mist_models as rmm

# load isochrones so data access is faster
# storing in a dictionary d[feh][vvc][gd_i] to access:
feh_range = [-0.30, -0.15, 0.00, 0.15, 0.30]
vvc_range = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
gdi_range = [0.0, 45.0, 90.0]
isocmds = {}
for feh_val in feh_range:
    # populate with isochrones at v/vc = 0.0...0.6 for each feh:
    i = {}
    for vvc_val in vvc_range:
        # populate with isochrones at gd_i = 0.0...0.90 for each v/vc:
        j = {}
        for gdi_val in gdi_range:
            j[gdi_val] = rmm.ISOCMD(feh=feh_val, vvcrit=vvc_val, gravdark_i=gdi_val, exttag='TP')
            # log10 age  = 8.5 is used as the default age.
            j[gdi_val].set_isodata(8.5, 'Tycho_B-Tycho_V', 'Tycho_V', dmod=0.0)
        i[vvc_val] = j
            
    isocmds[feh_val] = i

# Use feh = 0.00, v/vc = 0.0, i=0.0 as default isochrone
x = isocmds[0.00][0.0][0.0].x
y = isocmds[0.00][0.0][0.0].y

# A reference CMD to compare to (feh = 0.0, v/vc = 0.0, i = 0.0,  age = 8.0):
x_label = 'Tycho_B-Tycho_V'
y_label = 'Tycho_V'
x_ref, y_ref = (isocmds[0.00][0.0][0.0].get_data([x_label, y_label], [],
                                            lage = 8.0, dmod=0.0)).values()


# data source for main iso and reference:
source = ColumnDataSource(data=dict(x=x, y=y))
source_ref = ColumnDataSource(data=dict(x=x_ref, y=y_ref))


# Set up plot:
plot = figure(plot_height=800, plot_width=800,
              tools="crosshair,pan,reset,save,wheel_zoom",
              x_range=[x.min(), x.max()], y_range=[y.max(), y.min()])

plot.line('x', 'y', source=source, line_width=1, line_alpha=0.6)
plot.line('x', 'y', source=source_ref, line_width=1, line_alpha=0.6,
          line_color='black', line_dash="4 4")

# x, y axis labels:
plot.xaxis.axis_label = x_label
plot.yaxis.axis_label = y_label

# Set up widgets
# for data:
lage = Slider(title="log(age)", value=8.5, start=7.5, end=10.0, step=0.02)
vvc = Slider(title=r"V/Vc", value=0.0, start=0.0, end=0.6, step=0.1)
feh = Slider(title="[Fe/H]", value=0.0, start=-0.30, end=0.30, step=0.15)
gdi = Slider(title="i [deg]", value=0.0, start=0.0, end=90.0, step=45.0)

lage_ref = Slider(title="log(age) (reference)", value=8.0, start=7.5, end=10.0, step=0.02)
vvc_ref = Slider(title=r"V/Vc (reference)", value=0.0, start=0.0, end=0.6, step=0.1)
feh_ref = Slider(title="[Fe/H] (reference)", value=0.0, start=-0.30, end=0.30, step=0.15)
gdi_ref = Slider(title="i [deg] (reference)", value=0.0, start=0.0, end=90.0, step=45.0)

# for labels (filters):
lbl_ops = ['None', '-', '+', '*', '/']
filters_optional = ['None']
filters = []
for afilter in isocmds[0.00][0.0][0.0].hdr_list[9:-1]:
    filters.append(afilter)
    filters_optional.append(afilter)

x_lbl1 = Select(title="x-axis value 1", value='Tycho_B', options = filters)
x_op_title = Div(text="""x-axis operator (optional)""", height=10, width=200)
x_op = RadioButtonGroup(active=1, labels = lbl_ops)
x_lbl2 = Select(title="x-axis value 2 (optional)", value='Tycho_V', options = filters_optional)

y_lbl1 = Select(title="y-axis value 1", value='Tycho_V', options = filters)
y_op_title = Div(text="""y-axis operator (optional)""", height=10, width=200)
y_op = RadioButtonGroup(active=0, labels = lbl_ops)
y_lbl2 = Select(title="y-axis value 2 (optional)", value='None', options = filters_optional)

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
    
    lar = float("{:.2f}".format(lage_ref.value))
    vr = float("{:.1f}".format(vvc_ref.value))
    mr = float("{:.2f}".format(feh_ref.value))    
    ir = float("{:.1f}".format(gdi_ref.value))

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
    
    df = isocmds[m][v][i].get_data([x_label, y_label], [], lage = la, dmod=0.0)
    df_ref = isocmds[mr][vr][ir].get_data([x_label, y_label], [], lage = lar, dmod=0.0)
    
    # Generate the new curve
    x, y = df.values()
    xr,yr = df_ref.values()
    
    source.data = dict(x=x, y=y)
    source_ref.data = dict(x=xr, y=yr)

    plot.xaxis.axis_label = x_label
    plot.yaxis.axis_label = y_label

# update values on change via widgets:
for w in [lage, vvc, feh, gdi, lage_ref, vvc_ref, feh_ref,
          gdi_ref, x_lbl1, x_lbl2, y_lbl1, y_lbl2]:
    
    w.on_change('value', update_data)

x_op.on_change('active', update_data)
y_op.on_change('active', update_data)
    
# Set up layouts and add to document
inputs = widgetbox(lage, vvc, feh, gdi, lage_ref, vvc_ref, feh_ref, gdi_ref,
                   x_lbl1, x_op_title, x_op, x_lbl2, y_lbl1, y_op_title, y_op, y_lbl2)

curdoc().add_root(row(inputs, plot, width=800))
curdoc().title = "Isochrone Explorer"
