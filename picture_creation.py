import tecplot_lib
import numpy as np
import os

cwd = os.getcwd()
data_files_dir = os.path.join(os.path.dirname(cwd), 'boundary_layer_on_plate', 'tecplot_data_files')
picture_dir = os.path.join(cwd, 'pictures')
ny = - 35 / np.sqrt(35**2 + 30**2)
nz = 30 / np.sqrt(35**2 + 30**2)
slice_settings = tecplot_lib.SliceSettings(tecplot_lib.SliceType.ARBITRARY, position=(0, 0, 0), normal=(0, ny, nz))
level_settings = tecplot_lib.LevelSettings(variable_number=5, min_level=0, max_level=100, num_levels=21)
colormap_settings = tecplot_lib.ColormapSettings(color_distribution=tecplot_lib.ColorDistribution.BANDED,
                                                 colormap_name=tecplot_lib.ColorMap.MODERN)
export_settings = tecplot_lib.ExportSettings(zone_number=2, exportfname=os.path.join(picture_dir, 'test2.png'),
                                             imagewidth=1500)
legend_header_font = tecplot_lib.Font(font_family='Helvetica', is_bold=True, is_italic=False, height=7)
legend_number_font = tecplot_lib.Font(font_family='Helvetica', is_bold=True, is_italic=False, height=3)

legend_settings = tecplot_lib.LegendSettings(xy_position=(95, 65), rowspacing=1.2, auto_levelskip=1,
                                             isvertical=True, header_font=legend_header_font,
                                             number_font=legend_number_font)
x_title_font = tecplot_lib.Font(font_family='Helvetica', is_bold=True, is_italic=False, height=5)
x_label_font = tecplot_lib.Font(font_family='Helvetica', is_bold=True, is_italic=False, height=2.5)
y_title_font = tecplot_lib.Font(font_family='Helvetica', is_bold=True, is_italic=False, height=5)
y_label_font = tecplot_lib.Font(font_family='Helvetica', is_bold=True, is_italic=False, height=2.5)

axis_settings = tecplot_lib.AxisSettings(x_axis_var=22, y_axis_var=24, rect=(10, 10, 80, 40),
                                         x_title_font=x_title_font, x_label_font=x_label_font,
                                         x_title_offset=5, y_title_font=y_title_font, y_label_font=y_label_font,
                                         y_title_offset=5, xlim=(-0.1, 8.1), ylim=(-0.05, 0.4))

if __name__ == '__main__':
    file_for_picture = os.path.join(data_files_dir, 'average_grid_density_sp_al.lay')
    macro_name = os.path.join(cwd, 'macros', 'picture_creation2.mcr')
    picture_creator = tecplot_lib.PictureCreator(file_for_pictures=file_for_picture,
                                                 macro_filename=macro_name,
                                                 slice_settings=slice_settings, level_settings=level_settings,
                                                 legend_settings=legend_settings, colormap_settings=colormap_settings,
                                                 axis_settings=axis_settings, export_settings=export_settings)
    picture_creator.run_creation()