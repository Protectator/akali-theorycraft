# Imports
import numpy as np
import matplotlib.pyplot as pl
import matplotlib as mpl
from ipywidgets import interact, widgets

# Defining most constant values and calculations
def base_ad(lv):
    return 58.376 + (lv-1) * 3.2

def raw_spell_dmg(base, ad_ratio = 0, ap_ratio = 0, ap = 0, ad = 0):
    return base + ad_ratio * ad + ap_ratio * ap

def net_magic_dmg(dmg, enemy_resist=0, pen_flat=0, pen_perc=0):
    if enemy_resist >= 0:
        final_resist = enemy_resist * (1 - pen_perc/100)
        final_resist = final_resist - pen_flat
        final_resist = final_resist if final_resist >= 0 else 0
        return dmg * (100 / (100 + final_resist))
    else:
        return dmg * (2 - (100 / (100 - enemy_resist)))
    
def net_physical_dmg_old(dmg, enemy_armor=0, pen_flat=0, pen_perc=0):
    if enemy_armor >= 0:
        final_resist = enemy_armor * (1 - pen_perc/100)
        final_resist = final_resist - pen_flat
        final_resist = final_resist if final_resist >= 0 else 0
        return dmg * (100 / (100 + final_resist))
    else:
        return dmg * (2 - (100 / (100 - enemy_armor)))
    
def net_physical_dmg_new(dmg, enemy_resist=0, lethality=0, pen_perc=0, enemy_lv=1):
    pen_flat = lethality * 0.4 + lethality * 0.6 * enemy_lv / 18
    if enemy_resist >= 0:
        final_resist = enemy_resist * (1 - pen_perc/100)
        final_resist = final_resist - pen_flat
        final_resist = final_resist if final_resist >= 0 else 0
        return dmg * (100 / (100 + final_resist))
    else:
        return dmg * (2 - (100 / (100 - enemy_resist)))

def p_old(ad=0, ap=0):
    return (0.06 + 0.01 * (ap / 6)) * ad

def q_old(level, ap=0, proc=False):
    if not proc:
        return [35, 55, 75, 95, 115][level] + 0.4 * ap
    else:
        return [45, 70, 95, 120, 145][level] + 0.5 * ap
    
def e_old(level, ad=0, ap=0):
    return [30, 55, 80, 105, 130][level] + 0.4 * ap + 0.6 * ad

def r_old(level, ad=0, ap=0):
    return [100, 175, 250][level] + 0.5 * ap

def p_new(level, ad=0, ap=0):
    return [10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 40, 50, 60, 70, 80, 90, 100][level] + 0.5 * ad + 0.5 * ap

def q_new(level, ap=0, proc=False):
    if proc:
        return [35, 55, 75, 95, 115][level] + 0.4 * ap
    else:
        return [45, 70, 95, 120, 145][level] + 0.5 * ap
    
def e_new(level, ap=0, bonus_ad=0):
    return [70, 100, 130, 160, 190][level] + 0.5 * ap + 0.7 * bonus_ad

def r_new(level, ad=0, ap=0):
    return [50, 100, 150][level] + 0.25 * ap

ap_range = np.linspace(0, 600, 30)

# Computing the Passive - Twin Disciplines 
def p(enemy_mr, pen_flat, pen_perc, bonus_ad):
    p_old_dmg = []
    p_new_dmg = []
    for akali_lv in range(0,18):
        p_old_dmg.append([])
        p_new_dmg.append([])
        for ap in ap_range:
            p_old_raw = p_old(ad=base_ad(akali_lv) + bonus_ad, ap=np.asscalar(ap))
            p_new_raw = p_new(akali_lv, ad=base_ad(akali_lv) + bonus_ad, ap=np.asscalar(ap))
            p_old_dmg[akali_lv].append(net_magic_dmg(p_old_raw, enemy_mr, pen_flat, pen_perc))
            p_new_dmg[akali_lv].append(net_magic_dmg(p_new_raw, enemy_mr, pen_flat, pen_perc))
    pl.figure(figsize=(16,9))
    pl.xlabel('AP')
    pl.ylabel('Damages')
    pl.title("Akali's P [" + str(int(bonus_ad)) +  "bonus AD, " + str(int(pen_flat)) + "MPen, " +
             str(int(pen_perc)) + "%MPen vs " + str(int(enemy_mr)) + "MR target]")
    pl.grid()
    plots_old = []
    plots_new = []
    for lv in range(0,18):
        s = [0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95,1,1,1,1,1,1,1,1,1,1][lv]
        v = [1,1,1,1,1,1,1,1,1,1,0.95,0.9,0.85,0.8,0.75,0.7,0.65,0.6][lv]
        color_old = mpl.colors.hsv_to_rgb((0.6, s, v))
        color_new = mpl.colors.hsv_to_rgb((0, s, v))
        handles_old, = pl.plot(ap_range, p_old_dmg[lv], color=color_old, label='old', lw=2)
        handles_new, = pl.plot(ap_range, p_new_dmg[lv], color=color_new, label='new', lw=2)
        plots_old.append(handles_old)
        plots_new.append(handles_new)
    pl.legend(loc='upper left', handles=[plots_old[8], plots_new[8]])
    axes = pl.gca()
    ylim = axes.get_ylim()
    new_ylim = (0, ylim[1])
    axes.set_ylim(new_ylim)
    
# Computing the Q spell - Mark of the Assassin
def q(enemy_mr, magic_pen, magic_pen_perc):
    q_old_initial = []
    q_old_proc = []
    q_old_total = []
    for lv in range(0,5):
        q_old_initial.append([])
        q_old_proc.append([])
        q_old_total.append([])
        for ap in ap_range:
            initial = net_magic_dmg(q_old(lv, np.asscalar(ap)), enemy_mr, magic_pen, magic_pen_perc)
            proc = net_magic_dmg(q_old(lv, np.asscalar(ap), proc=True), enemy_mr, magic_pen, magic_pen_perc)
            q_old_initial[lv].append(initial)
            q_old_proc[lv].append(proc)
            q_old_total[lv].append(initial + proc)
    
    pl.figure(figsize=(16,6))
    
    subnumber = 1
    parts = ['initial', 'proc', 'total']
    for sub in [q_old_initial, q_old_proc, q_old_total]:
        pl.subplot(1, 3, subnumber)
        pl.xlabel('AP')
        pl.ylabel('Damages')
        pl.title("Akali's Q " + parts[subnumber-1] + " [" + str(int(magic_pen)) + "MPen, " +
                 str(int(magic_pen_perc)) + "%MPen vs " + str(int(enemy_mr)) + "MR]")
        pl.grid()
        plots = []
        for level in range(0,5):
            color_plot = mpl.colors.hsv_to_rgb((0.6, [0.6,0.8,1,1,1][level], [1,1,1,0.8,0.6][level]))
            handle, = pl.plot(ap_range, sub[level], color=color_plot, label='old unchanged', lw=2)
            plots.append(handle)
        axes = pl.gca()
        ylim = axes.get_ylim()
        new_ylim = (0, ylim[1])
        axes.set_ylim(new_ylim)
        pl.legend(loc='upper left', handles=[plots[2]])
        
        subnumber += 1

# Computing E - Crescent Slash
def e(enemy_armor, pen_flat, lethality, pen_perc, enemy_lv, akali_lv, bonus_ad):
    e_old_dmg = []
    e_new_dmg = []
    for lv in range(0,5):
        e_old_dmg.append([])
        e_new_dmg.append([])
        for ap in ap_range:
            e_old_raw = e_old(lv, ad=base_ad(akali_lv) + bonus_ad, ap=np.asscalar(ap))
            e_new_raw = e_new(lv, ap=np.asscalar(ap), bonus_ad=bonus_ad)
            e_old_dmg[lv].append(net_physical_dmg_old(e_old_raw, enemy_armor, pen_flat, pen_perc))
            e_new_dmg[lv].append(net_physical_dmg_new(e_new_raw, enemy_armor, lethality, pen_perc, enemy_lv))
    pl.figure(figsize=(16,9))
    pl.xlabel('AP')
    pl.ylabel('Damages')
    pl.title("Akali's E [" + str(int(base_ad(akali_lv))) + "+"
             + str(int(bonus_ad)) + "AD, " + str(int(pen_flat)) + "ArPen|" + str(int(lethality)) + "Lethality, " +
             str(int(pen_perc)) + "%ArPen vs " + str(int(enemy_armor)) + "Armor, lv" + str(int(enemy_lv)) + " target]")
    pl.grid()
    plots_old = []
    plots_new = []
    for lv in range(0,5):
        s = [0.6,0.8,1,1,1][lv]
        v = [1,1,1,0.8,0.6][lv]
        color_old = mpl.colors.hsv_to_rgb((0.6, s, v))
        color_new = mpl.colors.hsv_to_rgb((0, s, v))
        handles_old, = pl.plot(ap_range, e_old_dmg[lv], color=color_old, label='old', lw=2)
        handles_new, = pl.plot(ap_range, e_new_dmg[lv], color=color_new, label='new', lw=2)
        plots_old.append(handles_old)
        plots_new.append(handles_new)
    pl.legend(loc='upper left', handles=[plots_old[2], plots_new[2]])
    axes = pl.gca()
    ylim = axes.get_ylim()
    new_ylim = (0, ylim[1])
    axes.set_ylim(new_ylim)
    
# Computing R - Shadow Dance
def r(enemy_mr, pen_flat, pen_perc):
    r_old_dmg = []
    r_new_dmg = []
    for lv in range(0,3):
        r_old_dmg.append([])
        r_new_dmg.append([])
        for ap in ap_range:
            r_old_raw = r_old(lv, ap=np.asscalar(ap))
            r_new_raw = r_new(lv, ap=np.asscalar(ap))
            r_old_dmg[lv].append(net_magic_dmg(r_old_raw, enemy_mr, pen_flat, pen_perc))
            r_new_dmg[lv].append(net_magic_dmg(r_new_raw, enemy_mr, pen_flat, pen_perc))
    pl.figure(figsize=(16,9))
    pl.xlabel('AP')
    pl.ylabel('Damages')
    pl.title("Akali's R [" + str(int(pen_flat)) + "MPen, " +
             str(int(pen_perc)) + "%MPen vs " + str(int(enemy_mr)) + "MR target]")
    pl.grid()
    plots_old = []
    plots_new = []
    for lv in range(0,3):
        s = [0.6,1,1][lv]
        v = [1,1,0.6][lv]
        color_old = mpl.colors.hsv_to_rgb((0.6, s, v))
        color_new = mpl.colors.hsv_to_rgb((0, s, v))
        handles_old, = pl.plot(ap_range, r_old_dmg[lv], color=color_old, label='old', lw=2)
        handles_new, = pl.plot(ap_range, r_new_dmg[lv], color=color_new, label='new', lw=2)
        plots_old.append(handles_old)
        plots_new.append(handles_new)
    pl.legend(loc='upper left', handles=[plots_old[1], plots_new[1]])
    axes = pl.gca()
    ylim = axes.get_ylim()
    new_ylim = (0, ylim[1])
    axes.set_ylim(new_ylim)
    
# Showing graphs and interactions
def show_p():
    interact(p,
    bonus_ad=widgets.FloatSlider(value=0, min=0, max=400, step=5, description='Bonus AD',continuous_update=False),
    enemy_mr=widgets.FloatSlider(value=30, min=30, max=400, step=5, description='Enemy MR',continuous_update=False),
    pen_flat=widgets.FloatSlider(value=0, min=0, max=60, step=1, description='Magic Penetration',continuous_update=False),
    pen_perc=widgets.FloatSlider(value=0, min=0, max=100, step=1, description='Magic Penetration %',continuous_update=False));
    
def show_q():
    interact(q, enemy_mr=widgets.FloatSlider(value=30, min=30, max=400, step=5, description='Enemy MR',),
    magic_pen=widgets.FloatSlider(value=0, min=0, max=60, step=1, description='Magic Penetration',),
    magic_pen_perc=widgets.FloatSlider(value=0, min=0, max=100, step=1, description='Magic Penetration %',));
    
def show_e():
    interact(e,
    akali_lv=widgets.FloatSlider(value=1, min=1, max=18, step=1, description='Akali Level',continuous_update=False),
    enemy_lv=widgets.FloatSlider(value=1, min=1, max=18, step=1, description='Enemy Level',continuous_update=False),
    bonus_ad=widgets.FloatSlider(value=0, min=0, max=400, step=5, description='Bonus AD',continuous_update=False),
    enemy_armor=widgets.FloatSlider(value=30, min=30, max=400, step=5, description='Enemy Armor',continuous_update=False),
    pen_flat=widgets.FloatSlider(value=0, min=0, max=60, step=1, description='Armor Penetration',continuous_update=False),
    lethality=widgets.FloatSlider(value=0, min=0, max=60, step=1, description='Lethality',continuous_update=False),
    pen_perc=widgets.FloatSlider(value=0, min=0, max=100, step=1, description='Armor Penetration %',continuous_update=False));
    
def show_r():
    interact(r,
    enemy_mr=widgets.FloatSlider(value=30, min=30, max=400, step=5, description='Enemy MR',continuous_update=False),
    pen_flat=widgets.FloatSlider(value=0, min=0, max=60, step=1, description='Magic Penetration',continuous_update=False),
    pen_perc=widgets.FloatSlider(value=0, min=0, max=100, step=1, description='Magic Penetration %',continuous_update=False));