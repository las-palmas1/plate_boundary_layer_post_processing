import tecplot_lib
import os

if __name__ == '__main__':
    cwd = os.getcwd()
    data_files_dir = os.path.join(os.path.dirname(cwd), 'boundary_layer_on_plate', 'tecplot_data_files')
    data_file_name = os.path.join(data_files_dir, 'average_grid_density_sp_al.plt')
    open_file = tecplot_lib.get_open_data_file_command(data_file_name)
    alter_data1 = tecplot_lib.get_alterdata_command(equation='{X/h} = {X}')
    alter_data2 = tecplot_lib.get_alterdata_command(equation='{Y/h} = {Y}')
    alter_data3 = tecplot_lib.get_alterdata_command(equation='{Z/h} = {Z}')
    save = tecplot_lib.get_save_layout_command(os.path.splitext(data_file_name)[0] + '.lay')
    macro = tecplot_lib.wrap_macro(open_file + alter_data1 + alter_data2 + alter_data3 + save)
    macro_name = r'macros\alterdata.mcr'
    tecplot_lib.create_macro_file(macro, macro_name)
    tecplot_lib.execute_macro(macro_name)

