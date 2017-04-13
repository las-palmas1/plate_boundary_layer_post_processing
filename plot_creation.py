from tecplot_lib import LineDataFileLoader
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.optimize import fsolve


cfx_loader = LineDataFileLoader(r'extracted_data\cfx')
cfx_loader.load()

ace_loader = LineDataFileLoader(r'extracted_data\ace')
ace_loader.load()

cfx_very_high_dens_k_eps_i1_outlet_frames = cfx_loader.frames[0:3]

av_grid_dens_sp_al_frames = ace_loader.frames[0:3]
high_grid_dens_k_eps_two_layer_frames = ace_loader.frames[3:6]
high_grid_dens_k_eps_frames = ace_loader.frames[6:9]
high_grid_dens_sp_al_frames = ace_loader.frames[9:12]
very_high_grid_dens_k_eps_farfield_frames = ace_loader.frames[12:15]
very_high_grid_dens_k_eps_frames = ace_loader.frames[15:18]
very_high_grid_dens_k_eps_two_layer_farfield_frames = ace_loader.frames[18:21]
very_high_grid_dens_sp_al_farfield_frames = ace_loader.frames[21:24]
very_high_grid_dens_sp_al_frames = ace_loader.frames[24:27]

plots_dir = 'plots'

# скорость для определения коэффициента трения
u_ref_ace = 85
u_ref_cfx = 88

# скорость в ядре потока
U0 = ace_loader.frames[0].U[len(ace_loader.frames[0]) - 1]
# динамическая вязкость в ядре потока
Vislam0 = ace_loader.frames[0].Vislam[len(ace_loader.frames[0]) - 1]
# плотность в ядре потока
RHO0 = ace_loader.frames[0].RHO[len(ace_loader.frames[0]) - 1]


def get_tau(skin_friction_coefficient, core_density, core_velocity):
    return 0.5 * core_density * core_velocity ** 2 * skin_friction_coefficient


def get_schlichting_friction_coefficient(reynolds_number):
    return (2 * np.log10(reynolds_number) - 0.65) ** (-2.3)


def get_schultz_grunov_friction_coefficient(reynolds_number):
    return 0.37 * (np.log10(reynolds_number)) ** (-2.584)


def get_prandtl_friction_coefficient(reynolds_number):
    return 0.074 * reynolds_number ** (- 1 / 5)


def get_hughes_friction_coefficient(reynolds_number):
    return 0.067 * (np.log10(reynolds_number) - 2) ** (-2)

y0 = fsolve(lambda X: [2.5 * np.log(X[0] / 0.13) - X[0]], np.array([10]))[0]


def get_u_plus_theory(y_plus: np.ndarray):
    return 2.5 * np.log(y_plus / 0.13) * (y_plus > y0) + y_plus * (y_plus <= y0)


def plot_u_plus_theory():
    y_plus = np.array(np.logspace(0, 5, 2500))
    plt.plot(y_plus, get_u_plus_theory(y_plus),
             lw=2, color='black', label=r'$Теоретическая\ зависимость$', linestyle=':')


def set_velocity_profile_plot():
    plt.grid()
    plt.legend(fontsize=12)
    plt.xlabel(r'$U,\ м/с$', fontsize=14)
    plt.ylabel(r'$Z,\ м$', fontsize=14)


def set_friction_coefficient_plot(ylim=(0., 0.03)):
    plt.grid()
    plt.legend(fontsize=10)
    plt.ylim(*ylim)
    plt.xlim(0, 8)
    plt.xlabel(r'$X,\ м$', fontsize=14)
    plt.ylabel(r'$C_f$', fontsize=14)


def set_u_plus_plot():
    plt.xlabel(r'$Y^+$', fontsize=14)
    plt.ylabel(r'$U^+$', fontsize=14)
    plt.grid()
    plt.xscale('log')
    plt.legend(fontsize=10)
    plt.xlim(1, 10e2)
    plt.ylim(0, 25)

X = np.array(np.linspace(0, 8,  1500))
Re_x = RHO0 * X * U0 / Vislam0
Cf_Schlichting = get_schlichting_friction_coefficient(Re_x)
Cf_Schultz_Grunov = get_schultz_grunov_friction_coefficient(Re_x)
Cf_Prandtl = get_prandtl_friction_coefficient(Re_x)
Cf_Hughes = get_hughes_friction_coefficient(Re_x)
TAU_Schlichting = get_tau(Cf_Schlichting, RHO0, U0)
TAU_Schultz_Grunov = get_tau(Cf_Schultz_Grunov, RHO0, U0)
TAU_Prandtl = get_tau(Cf_Prandtl, RHO0, U0)
TAU_Hughes = get_tau(Cf_Hughes, RHO0, U0)


def plot_friction_coefficient_theory():
    X = np.linspace(0, 8,  1500)
    plt.plot(X, Cf_Schlichting, lw=1, color='red',
             label=r'$Формула\ Шлихтинга$', linestyle='--')
    plt.plot(X, Cf_Schultz_Grunov, lw=1, color='blue',
             label=r'$Формула\ Шульца-Грунова$', linestyle='--')
    plt.plot(X, Cf_Prandtl, lw=1, color='green',
             label=r'$Формула\ Прандтля$', linestyle='--')
    plt.plot(X, Cf_Hughes, lw=1, color='red',
             label=r'$Формула\ Хьюза$', linestyle=':')


for frame in ace_loader.frames:
    if frame.ix[frame.Z == 0].__len__() == 1:
        RHO = frame.ix[frame.Z == 0].RHO[0]
        SkinFrictionCoefficient = frame.ix[frame.Z == 0].SkinFrictionCoefficient[0]
        Vislam = frame.ix[frame.Z == 0].Vislam[0]
        VIS_T = frame.ix[frame.Z == 0].VIS_T[0]
    else:
        RHO = frame.ix[frame.Z == 0].RHO
        SkinFrictionCoefficient = frame.ix[frame.Z == 0].SkinFrictionCoefficient
        Vislam = frame.ix[frame.Z == 0].Vislam
        VIS_T = frame.ix[frame.Z == 0].VIS_T
    frame['UPLUS'] = frame.U / u_ref_ace * np.sqrt(2 / SkinFrictionCoefficient)
    frame['YPLUSPrime'] = RHO / Vislam * frame.Z * u_ref_ace * np.sqrt(SkinFrictionCoefficient / 2)
    frame['TAU'] = 0.5 * RHO * u_ref_ace ** 2 * SkinFrictionCoefficient


for frame in cfx_loader.frames:
    frame['SkinFrictionCoefficient'] = 2 * frame['X Wall Shear'] / (frame.Density * u_ref_ace ** 2)
    if frame.ix[frame.Z == 0].__len__() == 1:
        RHO = frame.ix[frame.Z == 0].Density[0]
        SkinFrictionCoefficient = frame.ix[frame.Z == 0].SkinFrictionCoefficient[0]
        Vislam = frame.ix[frame.Z == 0]['Dynamic Viscosity'][0]
        VIS_T = frame.ix[frame.Z == 0]['Eddy Viscosity'][0]
    else:
        RHO = frame.ix[frame.Z == 0].Density
        SkinFrictionCoefficient = frame.ix[frame.Z == 0].SkinFrictionCoefficient
        Vislam = frame.ix[frame.Z == 0]['Dynamic Viscosity']
        VIS_T = frame.ix[frame.Z == 0]['Eddy Viscosity']
    frame['UPLUS'] = frame.U / u_ref_cfx * np.sqrt(2 / SkinFrictionCoefficient)
    frame['YPLUSPrime'] = RHO / Vislam * frame.Z * u_ref_cfx * np.sqrt(SkinFrictionCoefficient / 2)
    frame['TAU'] = 0.5 * RHO * u_ref_cfx ** 2 * SkinFrictionCoefficient

# --------------------------------------------------------------------------------------------
#  графики для сеток с различными густотами
# --------------------------------------------------------------------------------------------

# ////////////////
# модель Спаларта
# ////////////////

plt.figure(figsize=(8, 6))
plt.plot(av_grid_dens_sp_al_frames[0].U, av_grid_dens_sp_al_frames[0].Z, lw=2, color='red',
         label=r'$Средняя\ плотность\ сетки$')
plt.plot(high_grid_dens_sp_al_frames[0].U, high_grid_dens_sp_al_frames[0].Z, lw=2, color='blue',
         label=r'$Высокая\ плотность\ сетки$', linestyle='-')
plt.plot(very_high_grid_dens_sp_al_frames[0].U, very_high_grid_dens_sp_al_frames[0].Z, lw=2, color='green',
         label=r'$Очень\ высокая\ плотность\ сетки$', linestyle='-')
plt.title(r'$Модель\ Спаларта$')
set_velocity_profile_plot()
plt.savefig(os.path.join(plots_dir, 'density_comparison_sp_al_U_profile_line_0.png'))


plt.figure(figsize=(8, 6))
plt.plot(av_grid_dens_sp_al_frames[1].YPLUSPrime, av_grid_dens_sp_al_frames[1].UPLUS, lw=2, color='red',
         label=r'$Средняя\ плотность\ сетки$')
plt.plot(high_grid_dens_sp_al_frames[1].YPLUSPrime, high_grid_dens_sp_al_frames[1].UPLUS, lw=2, color='blue',
         label=r'$Высокая\ плотность\ сетки$')
plt.plot(very_high_grid_dens_sp_al_frames[1].YPLUSPrime, very_high_grid_dens_sp_al_frames[1].UPLUS, lw=2, color='green',
         label=r'$Очень\ высокая\ плотность\ сетки$')
plot_u_plus_theory()
plt.title(r'$Модель\ Спаларта$')
set_u_plus_plot()
plt.savefig(os.path.join(plots_dir, 'density_comparison_sp_al_UPLUS_YPLUS_log_profile_line_1.png'))


plt.figure(figsize=(8, 6))
plt.plot(av_grid_dens_sp_al_frames[2].X, av_grid_dens_sp_al_frames[2].SkinFrictionCoefficient, lw=2, color='red',
         label=r'$Средняя\ плотность\ сетки$')
plt.plot(high_grid_dens_sp_al_frames[2].X, high_grid_dens_sp_al_frames[2].SkinFrictionCoefficient, lw=2, color='blue',
         label=r'$Высокая\ плотность\ сетки$')
plt.plot(very_high_grid_dens_sp_al_frames[2].X, very_high_grid_dens_sp_al_frames[2].SkinFrictionCoefficient, lw=2,
         color='green', label=r'$Очень\ высокая\ плотность\ сетки$')
plot_friction_coefficient_theory()
plt.title(r'$Модель\ Спаларта$')
set_friction_coefficient_plot()
plt.savefig(os.path.join(plots_dir, 'density_comparison_sp_al_friction_coefficient_profile.png'))

# ////////////////
# модель k-e
# ////////////////

plt.figure(figsize=(8, 6))
plt.plot(high_grid_dens_k_eps_frames[0].U, high_grid_dens_k_eps_frames[0].Z, lw=2, color='blue',
         label=r'$Высокая\ плотность\ сетки$', linestyle='-')
plt.plot(very_high_grid_dens_k_eps_frames[0].U, very_high_grid_dens_k_eps_frames[0].Z, lw=2, color='green',
         label=r'$Очень\ высокая\ плотность\ сетки$', linestyle='-')
plt.title(r'$k-\varepsilon\ модель$')
set_velocity_profile_plot()
plt.savefig(os.path.join(plots_dir, 'density_comparison_k_eps_U_profile_line_0.png'))


plt.figure(figsize=(8, 6))
plt.plot(high_grid_dens_k_eps_frames[1].YPLUSPrime, high_grid_dens_k_eps_frames[1].UPLUS, lw=2, color='blue',
         label=r'$Высокая\ плотность\ сетки$')
plt.plot(very_high_grid_dens_k_eps_frames[1].YPLUSPrime, very_high_grid_dens_k_eps_frames[1].UPLUS, lw=2, color='green',
         label=r'$Очень\ высокая\ плотность\ сетки$')
plot_u_plus_theory()
plt.title(r'$k-\varepsilon\ модель$')
set_u_plus_plot()
plt.savefig(os.path.join(plots_dir, 'density_comparison_k_eps_UPLUS_YPLUS_log_profile_line_1.png'))


plt.figure(figsize=(8, 6))
plt.plot(high_grid_dens_k_eps_frames[2].X, high_grid_dens_k_eps_frames[2].SkinFrictionCoefficient, lw=2, color='blue',
         label=r'$Высокая\ плотность\ сетки$')
plt.plot(very_high_grid_dens_k_eps_frames[2].X, very_high_grid_dens_k_eps_frames[2].SkinFrictionCoefficient, lw=2,
         color='green', label=r'$Очень\ высокая\ плотность\ сетки$')
plot_friction_coefficient_theory()
plt.title(r'$k-\varepsilon\ модель$')
set_friction_coefficient_plot()
plt.savefig(os.path.join(plots_dir, 'density_comparison_k_eps_friction_coefficient_profile.png'))


# -------------------------------------------------------------------------------------------------------
#  графики для различных моделей турбулентности
# --------------------------------------------------------------------------------------------------------

plt.figure(figsize=(8, 6))
plt.plot(very_high_grid_dens_sp_al_frames[0].U, very_high_grid_dens_sp_al_frames[0].Z, lw=2, color='red',
         label=r'$Модель\ Спаларта$')
plt.plot(very_high_grid_dens_k_eps_frames[0].U, very_high_grid_dens_k_eps_frames[0].Z, lw=2, color='blue',
         label=r'$k-\varepsilon\ модель$', linestyle='-')
plt.legend(fontsize=12)
set_velocity_profile_plot()
plt.savefig(os.path.join(plots_dir, 'turbulence_model_comparison_U_profile_line_0.png'))


plt.figure(figsize=(8, 6))
plt.plot(very_high_grid_dens_sp_al_frames[1].YPLUSPrime, very_high_grid_dens_sp_al_frames[1].UPLUS, lw=2, color='red',
         label=r'$Модель\ Спаларта$')
plt.plot(very_high_grid_dens_k_eps_frames[1].YPLUSPrime, very_high_grid_dens_k_eps_frames[1].UPLUS, lw=2, color='blue',
         label=r'$k-\varepsilon\ модель$')
plot_u_plus_theory()
set_u_plus_plot()
plt.savefig(os.path.join(plots_dir, 'turbulence_model_comparison_UPLUS_YPLUS_log_profile_line_1.png'))


plt.figure(figsize=(8, 6))
plt.plot(very_high_grid_dens_sp_al_frames[2].X, very_high_grid_dens_sp_al_frames[2].SkinFrictionCoefficient, lw=2,
         color='red', label=r'$Модель\ Спаларта$')
plt.plot(very_high_grid_dens_k_eps_frames[2].X, very_high_grid_dens_k_eps_frames[2].SkinFrictionCoefficient, lw=2,
         color='blue', label=r'$k-\varepsilon\ модель$')
plot_friction_coefficient_theory()
set_friction_coefficient_plot()
plt.savefig(os.path.join(plots_dir, 'turbulence_model_comparison_friction_coefficient_profile.png'))


# ---------------------------------------------------------------------------------------------------
#  графики для различных функций стенки
# ---------------------------------------------------------------------------------------------------

plt.figure(figsize=(8, 6))
plt.plot(high_grid_dens_k_eps_two_layer_frames[1].YPLUSPrime, high_grid_dens_k_eps_two_layer_frames[1].UPLUS, lw=2,
         color='red', label=r'$Two\ layer\ model$')
plt.plot(high_grid_dens_k_eps_frames[1].YPLUSPrime, high_grid_dens_k_eps_frames[1].UPLUS, lw=2, color='blue',
         label=r'$Standard\ wall$')
plot_u_plus_theory()
set_u_plus_plot()
plt.savefig(os.path.join(plots_dir, 'wall_function_comparison_UPLUS_YPLUS_log_profile_line_1.png'))


plt.figure(figsize=(8, 6))
plt.plot(high_grid_dens_k_eps_two_layer_frames[2].X, high_grid_dens_k_eps_two_layer_frames[2].SkinFrictionCoefficient,
         lw=2, color='red', label=r'$Two\ layer\ model$')
plt.plot(high_grid_dens_k_eps_frames[2].X, high_grid_dens_k_eps_frames[2].SkinFrictionCoefficient, lw=2,
         color='blue', label=r'$Standard\ wall$')
plot_friction_coefficient_theory()
set_friction_coefficient_plot()
plt.savefig(os.path.join(plots_dir, 'wall_function_comparison_friction_coefficient_profile.png'))


# -----------------------------------------------------------------------------------------------------------------
# графики для различных граничных условий
# -----------------------------------------------------------------------------------------------------------------

# ///////////////////////////
# модель Спаларта
# ///////////////////////////
plt.figure(figsize=(8, 6))
plt.plot(very_high_grid_dens_sp_al_farfield_frames[1].YPLUSPrime,
         very_high_grid_dens_sp_al_farfield_frames[1].UPLUS, lw=2,
         color='red', label=r'$Farfield\ condition$')
plt.plot(very_high_grid_dens_sp_al_frames[1].YPLUSPrime,
         very_high_grid_dens_sp_al_frames[1].UPLUS, lw=2, color='blue',
         label=r'$Symmetry\ condition$')
plot_u_plus_theory()
set_u_plus_plot()
plt.title(r'$Spalart\ model$', fontsize=14)
plt.savefig(os.path.join(plots_dir, 'bc_comparison_sp_al_UPLUS_YPLUS_log_profile_line_1.png'))

plt.figure(figsize=(8, 6))
plt.plot(very_high_grid_dens_sp_al_farfield_frames[2].X,
         very_high_grid_dens_sp_al_farfield_frames[2].SkinFrictionCoefficient,
         lw=2, color='red', label=r'$Farfield\ condition$')
plt.plot(very_high_grid_dens_sp_al_frames[2].X,
         very_high_grid_dens_sp_al_frames[2].SkinFrictionCoefficient, lw=2,
         color='blue', label=r'$Symmetry\ condition$')
plot_friction_coefficient_theory()
set_friction_coefficient_plot(ylim=(0., 0.008))
plt.title(r'$Spalart\ model$', fontsize=14)
plt.savefig(os.path.join(plots_dir, 'bc_comparison_sp_al_friction_coefficient_profile.png'))

# ///////////////////////////
# модель k-e, standard_wall
# ///////////////////////////
plt.figure(figsize=(8, 6))
plt.plot(very_high_grid_dens_k_eps_farfield_frames[1].YPLUSPrime,
         very_high_grid_dens_k_eps_farfield_frames[1].UPLUS, lw=2,
         color='red', label=r'$Farfield\ condition$')
plt.plot(very_high_grid_dens_k_eps_frames[1].YPLUSPrime,
         very_high_grid_dens_k_eps_frames[1].UPLUS, lw=2, color='blue',
         label=r'$Symmetry\ condition$')
plot_u_plus_theory()
set_u_plus_plot()
plt.title(r'$k-\varepsilon\ model,\ standard\ wall$', fontsize=14)
plt.savefig(os.path.join(plots_dir, 'bc_comparison_k_eps_UPLUS_YPLUS_log_profile_line_1.png'))

plt.figure(figsize=(8, 6))
plt.plot(very_high_grid_dens_k_eps_farfield_frames[2].X,
         very_high_grid_dens_k_eps_farfield_frames[2].SkinFrictionCoefficient,
         lw=2, color='red', label=r'$Farfield\ condition$')
plt.plot(very_high_grid_dens_k_eps_frames[2].X,
         very_high_grid_dens_k_eps_frames[2].SkinFrictionCoefficient, lw=2,
         color='blue', label=r'$Symmetry\ condition$')
plot_friction_coefficient_theory()
set_friction_coefficient_plot(ylim=(0., 0.025))
plt.title(r'$k-\varepsilon\ model,\ standard\ wall$', fontsize=14)
plt.savefig(os.path.join(plots_dir, 'bc_comparison_k_eps_friction_coefficient_profile.png'))

# ///////////////////////////
# модель k-e, two layer model
# ///////////////////////////
plt.figure(figsize=(8, 6))
plt.plot(very_high_grid_dens_k_eps_two_layer_farfield_frames[1].YPLUSPrime,
         very_high_grid_dens_k_eps_two_layer_farfield_frames[1].UPLUS, lw=2,
         color='red', label=r'$Farfield\ condition,\ very\ high\ density$')
plt.plot(high_grid_dens_k_eps_two_layer_frames[1].YPLUSPrime,
         high_grid_dens_k_eps_two_layer_frames[1].UPLUS, lw=2, color='blue',
         label=r'$Symmetry\ condition,\ high\ density$')
plot_u_plus_theory()
set_u_plus_plot()
plt.title(r'$k-\varepsilon\ model,\ two\ layer\ model$', fontsize=14)
plt.savefig(os.path.join(plots_dir, 'bc_comparison_k_eps_two_layer_UPLUS_YPLUS_log_profile_line_1.png'))

plt.figure(figsize=(8, 6))
plt.plot(very_high_grid_dens_k_eps_two_layer_farfield_frames[2].X,
         very_high_grid_dens_k_eps_two_layer_farfield_frames[2].SkinFrictionCoefficient,
         lw=2, color='red', label=r'$Farfield\ condition,\ very\ high\ density$')
plt.plot(high_grid_dens_k_eps_two_layer_frames[2].X,
         high_grid_dens_k_eps_two_layer_frames[2].SkinFrictionCoefficient, lw=2,
         color='blue', label=r'$Symmetry\ condition,\ high\ density$')
plot_friction_coefficient_theory()
set_friction_coefficient_plot(ylim=(0., 0.01))
plt.title(r'$k-\varepsilon\ model,\ two\ layer\ model$', fontsize=14)
plt.savefig(os.path.join(plots_dir, 'bc_comparison_k_eps_two_layer_friction_coefficient_profile.png'))


# ------------------------------------------------------------------------------------------------------
#  сравнение ace и cfx
# ------------------------------------------------------------------------------------------------------

# ///////////////////////////
# модель k-e
# ///////////////////////////
plt.figure(figsize=(8, 6))
plt.plot(very_high_grid_dens_k_eps_two_layer_farfield_frames[1].YPLUSPrime,
         very_high_grid_dens_k_eps_two_layer_farfield_frames[1].UPLUS, lw=2,
         color='red', label=r'$ACE-CFD,\ k-\varepsilon\ model,\ farfield\ bc$')
plt.plot(cfx_very_high_dens_k_eps_i1_outlet_frames[1].YPLUSPrime,
         cfx_very_high_dens_k_eps_i1_outlet_frames[1].UPLUS, lw=2, color='blue',
         label=r'$CFX,\ k-\varepsilon\ model,\ outlet\ bc$')
plot_u_plus_theory()
set_u_plus_plot()
plt.title('1.6M cells, turbulence intensity = 10%')
plt.savefig(os.path.join(plots_dir, 'ace_cfx_comparison_k_eps_int1_UPLUS_YPLUS_log_profile_line_1.png'))

plt.figure(figsize=(8, 6))
plt.plot(very_high_grid_dens_k_eps_two_layer_farfield_frames[2].X,
         very_high_grid_dens_k_eps_two_layer_farfield_frames[2].SkinFrictionCoefficient,
         lw=2, color='red', label=r'$ACE-CFD,\ k-\varepsilon\ model,\ farfield\ bc$')
plt.plot(cfx_very_high_dens_k_eps_i1_outlet_frames[2].X,
         cfx_very_high_dens_k_eps_i1_outlet_frames[2].SkinFrictionCoefficient, lw=2,
         color='blue', label=r'$CFX,\ k-\varepsilon\ model,\ outlet\ bc$')
plot_friction_coefficient_theory()
set_friction_coefficient_plot(ylim=(0., 0.01))
plt.title('1.6M cells, turbulence intensity = 10%')
plt.savefig(os.path.join(plots_dir, 'ace_cfx_comparison_k_eps_int1_friction_coefficient_profile.png'))

plt.show()
