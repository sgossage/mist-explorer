#from MIST_codes.scripts import read_mist_models as rmm



# select an isochrone object (w/ feh=0.00, selectable v/vc for now):
#isocmd = rmm.ISOCMD(vvcrit=vvc, exttag='TP')

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

'''
import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, TextInput
from bokeh.plotting import figure

from MIST_codes.scripts import read_mist_models as rmm

# load isochrones so data access is faster
# storing in a dictionary d[feh][vvc] to access:
feh_range = [-0.30, -0.15, 0.00, 0.15, 0.30]
vvc_range = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
gdi_range = [0.0, 45.0, 90.0]
isocmds = {}
for feh_val in feh_range:
    # populate with isochrones at v/vc = 0.0...0.6 for each feh:
    i = {}
    for vvc_val in vvc_range:
        #i[vvc_val] = rmm.ISOCMD(feh=feh_val, vvcrit=vvc_val, exttag='TP')
        # log10 age  = 8.5 is used as the default age.
        #i[vvc_val].set_isodata(8.5, 'Tycho_B-Tycho_V', 'Tycho_V', dmod=0.0)

        # populate with isochrones at gd_i = 0.0...0.90 for each v/vc:
        j = {}
        for gdi_val in gdi_range:
            j[gdi_val] = rmm.ISOCMD(feh=feh_val, vvcrit=vvc_val, gravdark_i=gdi_val, exttag='TP')
            # log10 age  = 8.5 is used as the default age.
            j[gdi_val].set_isodata(8.5, 'Tycho_B-Tycho_V', 'Tycho_V', dmod=0.0)
        i[vvc_val] = j
            
    isocmds[feh_val] = i

# Use feh = 0.00, v/vc = 0.0 as default isochrone
x = isocmds[0.00][0.0][0.0].x
y = isocmds[0.00][0.0][0.0].y

# A reference CMD to compare to (feh = 0.0, v/vc = 0.0, age = 8.0):
x_ref, y_ref = (isocmds[0.00][0.0][0.0].get_data(['Tycho_B-Tycho_V', 'Tycho_V'], [],
                                            lage = 8.0, dmod=0.0)).values()


# data source for main iso and reference:
source = ColumnDataSource(data=dict(x=x, y=y))
source_ref = ColumnDataSource(data=dict(x=x_ref, y=y_ref))


# Set up plot
plot = figure(plot_height=600, plot_width=800,
              tools="crosshair,pan,reset,save,wheel_zoom",
              x_range=[x.min(), x.max()], y_range=[y.max(), y.min()])

plot.line('x', 'y', source=source, line_width=1, line_alpha=0.6)
plot.line('x', 'y', source=source_ref, line_width=1, line_alpha=0.6,
          line_color='black', line_dash="4 4")


# Set up widgets
#text = TextInput(title="title", value='my sine wave')
lage = Slider(title="log(age)", value=8.5, start=7.5, end=10.0, step=0.02)
vvc = Slider(title=r"$\Omega/\Omega_c$", value=0.0, start=0.0, end=0.6, step=0.1)
feh = Slider(title="[Fe/H]", value=0.0, start=-0.30, end=0.30, step=0.15)
gdi = Slider(title="i [deg]", value=0.0, start=0.0, end=90.0, step=45.0)

lage_ref = Slider(title="log(age) (reference)", value=8.0, start=7.5, end=10.0, step=0.02)
vvc_ref = Slider(title=r"$\Omega/\Omega_c$ (reference)", value=0.0, start=0.0, end=0.6, step=0.1)
feh_ref = Slider(title="[Fe/H] (reference)", value=0.0, start=-0.30, end=0.30, step=0.15)
gdi_ref = Slider(title="i [deg] (reference)", value=0.0, start=0.0, end=90.0, step=45.0)

# Set up callbacks
#def update_title(attrname, old, new):
#    plot.title.text = text.value

#text.on_change('value', update_title)

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
    
    df = isocmds[m][v][i].get_data(['Tycho_B-Tycho_V', 'Tycho_V'], [], lage = la, dmod=0.0)
    df_ref = isocmds[mr][vr][ir].get_data(['Tycho_B-Tycho_V', 'Tycho_V'], [], lage = lar, dmod=0.0)
    
    # Generate the new curve
    x, y = df.values()
    xr,yr = df_ref.values()
    
    source.data = dict(x=x, y=y)
    source_ref.data = dict(x=xr, y=yr)

# update values on change via widgets:
for w in [lage, vvc, feh, gdi, lage_ref, vvc_ref, feh_ref, gdi_ref]:
    w.on_change('value', update_data)


# Set up layouts and add to document
inputs = widgetbox(lage, vvc, feh, gdi, lage_ref, vvc_ref, feh_ref, gdi_ref)

curdoc().add_root(row(inputs, plot, width=800))
curdoc().title = "Isochrone Explorer"
