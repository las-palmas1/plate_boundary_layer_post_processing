import typing
import os
import pandas as pd
import copy
import enum
import numpy as np


class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class PolyLine:
    def __init__(self, nodes: typing.List[Point], numpoints):
        self.nodes = nodes
        self.numpoints = numpoints


def wrap_macro(macro_body: str) -> str:
    result = "#!MC 1410\n" \
             "$!VarSet |MFBD| = 'C:\Program Files\Tecplot\Tecplot 360 EX 2016 R2'\n" \
             "%s"\
             "$!RemoveVar |MFBD|\n" \
             "$!Quit" % macro_body
    return result


def get_extract_from_polyline_command(polyline: PolyLine,
                                      filename) -> str:
    result = "$!EXTRACTFROMPOLYLINE\n" \
           "EXTRACTLINEPOINTSONLY = NO\n" \
           "EXTRACTTHROUGHVOLUME = YES\n" \
           "EXTRACTTOFILE = YES\n" \
           "FNAME = '%s'\n" \
           "NUMPTS = %s\n" \
           "RAWDATA\n" \
           "%s\n" % (filename, polyline.numpoints, len(polyline.nodes))
    template = "%s %s %s\n"
    for i in polyline.nodes:
        result += template % (i.x, i.y, i.z)
    return result


def get_open_data_file_command(filename):
    result = "$!READDATASET  '%s'\n" % filename
    return result


def get_open_layout_command(filename) -> str:
    result = "$!OPENLAYOUT  '%s'\n" % filename
    return result


def get_data_file_extraction_macro_body(filename, polylines: typing.List[PolyLine], output_dir) -> str:
    s1 = get_open_data_file_command(filename)
    s2 = ''
    output_filename_template = os.path.splitext(os.path.split(filename)[1])[0] + '_line_%s.dat'
    for n, polyline in enumerate(polylines):
        s2 += '%s' % (get_extract_from_polyline_command(polyline,
                                                        os.path.join(output_dir, output_filename_template) % n))
    return s1 + s2


def create_macro_file(macros: str, filename):
    file = open(filename, 'w')
    file.write(macros)
    file.close()


def execute_macro(filename):
    os.system(filename)


class LineDataExtractor:
    """
    Обеспечивает возможность создания макроса, извелающего из .plt файла данные по набору полилиний и
    сохраняющего эти данные в текстовые файлы с расширением .dat
    """
    def __init__(self, datafiles_dir, output_dir, polylines_list: typing.List[typing.List[PolyLine]], macro_name):
        """
        :param datafiles_dir: Имя директории, в которой располагаются .plt файлы
        :param output_dir: Имя директории для извлеченных данных
        :param polylines_list: список полилиний, по которым будут извелкаться данные
        :param macro_name: имя макроса, под которым он будет сохранен
        """
        self.datafiles_dir = datafiles_dir
        self.output_dir = output_dir
        self.polylines_list = polylines_list
        self.macro_name = macro_name

    def _get_macro(self) -> str:
        data_filenames = os.listdir(self.datafiles_dir)
        assert len(self.polylines_list) == len(data_filenames), 'Number of data files and number of sets of polylines '\
                                                                'must be same'
        macros_body = ''
        for n, filename in enumerate(data_filenames):
            macros_body += '%s' % get_data_file_extraction_macro_body(os.path.join(self.datafiles_dir, filename),
                                                                      self.polylines_list[n], self.output_dir)
        return wrap_macro(macros_body)

    def run_extraction(self):
        macro = self._get_macro()
        create_macro_file(macro, self.macro_name)
        execute_macro(self.macro_name)


class LineDataFileLoader:
    """
    Позволяет считать извлеченные по полилиниям данные  из всех файлов, содержащихся в папке, путь к которой 
     хранится в поле data_dirname, и записать данные из каждого файла в экземпляр класса Pandas.DataFrame, доступ к 
     списку которых осуществляется через поле frame
    """
    def __init__(self, data_dirname: str):
        """
        :param data_dirname: имя папки, содержащей файлы с извлеченными данными
        """
        self.data_dirname = data_dirname
        self.frames: typing.List[pd.DataFrame] = []

    @classmethod
    def _split_str(cls, string: str) -> typing.List[str]:
        arr = string.split(sep=' ')
        res = []
        for s in arr:
            if s != '' and s != '\n':
                res.append(s)
        return res

    @classmethod
    def _format_strings(cls, str_list: typing.List[str]) -> typing.List[str]:
        result = copy.deepcopy(str_list)
        for n, i in enumerate(str_list):
            result[n] = i.replace('\n', '').replace('"', '')
        return result

    @classmethod
    def _get_str_list_from_file(cls, filename) -> typing.List[typing.List[str]]:
        result = []
        file = open(filename, 'r')
        s = ' '
        while s != '':
            s = file.readline()
            result.append(cls._split_str(s))
        file.close()
        for n in range(len(result)):
            result[n] = cls._format_strings(result[n])
        return result

    @classmethod
    def _get_sum_str_list(cls, str_list: typing.List[str], start: int, with_spaces=False) -> str:
        result = ''
        for n, string in enumerate(str_list):
            if n >= start:
                if with_spaces:
                    result += string + ' '
                else:
                    result += string
        if with_spaces:
            result = result[0:(len(result) - 1)]
        return result

    @classmethod
    def _get_variable_names(cls, str_list: typing.List[typing.List[str]]) -> typing.List[str]:
        result = []
        for n, i in enumerate(str_list):
            if n == 0:
                result.append(cls._get_sum_str_list(i, 2, with_spaces=True))
            elif i[0] != 'ZONE':
                result.append(cls._get_sum_str_list(i, 0, with_spaces=True))
            elif i[0] == 'ZONE':
                break
        return result

    @classmethod
    def _get_variable_arrays(cls, str_list: typing.List[typing.List[str]]) -> typing.List[typing.List[float]]:
        result = []
        for n, i in enumerate(str_list):
            try:
                if len(i) > 0:
                    float(i[0])
                    result.append([])
                    for j in i:
                        result[len(result) - 1].append(float(j))
            except ValueError:
                pass
        return result

    def load(self):
        files_list = os.listdir(self.data_dirname)
        for filename in files_list:
            str_list = self._get_str_list_from_file(os.path.join(self.data_dirname, filename))
            var_names = self._get_variable_names(str_list)
            var_arrays = self._get_variable_arrays(str_list)
            self.frames.append(pd.DataFrame.from_records(var_arrays, columns=var_names))


class SliceType(enum.Enum):
    XPLANES = 0
    YPLANES = 1
    ZPLANES = 2
    IPLANES = 3
    JPLANES = 4
    KPLANES = 5
    ARBITRARY = 6


def get_slice_setting_macro(slice_type: SliceType, position: tuple, **kwargs) -> str:
    position_template = '%s = %s %s = %s %s = %s'
    primary_position = ''
    if slice_type == SliceType.XPLANES or slice_type == SliceType.YPLANES or slice_type == SliceType.ZPLANES or \
       slice_type == SliceType.ARBITRARY:
        primary_position = position_template % ('X', position[0], 'Y', position[1], 'Z', position[2])
    elif slice_type == SliceType.IPLANES or slice_type == SliceType.JPLANES or slice_type == SliceType.KPLANES:
        primary_position = position_template % ('I', position[0], 'J', position[1], 'K', position[2])

    if slice_type == SliceType.ARBITRARY and 'normal' not in kwargs:
        assert 'normal' in kwargs, 'Normal vector must be specified'
    normal_string = ''
    if slice_type == SliceType.ARBITRARY and 'normal' in kwargs:
        normal_string = '$!SLICEATTRIBUTES 1 NORMAl {X = %s Y = %s Z = %s}\n' % (kwargs['normal'][0],
                                                                                 kwargs['normal'][1],
                                                                                 kwargs['normal'][2])
    result = "$!SLICELAYERS SHOW = YES\n" \
             "$!SLICEATTRIBUTES 1  SLICESURFACE = %s\n" \
             "$!SLICEATTRIBUTES 1  PRIMARYPOSITION{%s}\n" % (slice_type.name, primary_position) + normal_string
    return result


class Variable(enum.Enum):
    X = 1
    Y = 2
    Z = 3


def get_go_to_2d_macro(x_axis_var: Variable, y_axis_var: Variable, rect: tuple = (10, 10, 90, 90), **kwargs) -> str:
    """
    :param x_axis_var:
    :param y_axis_var:
    :param rect: определяет положение прямоугольника сетки на frame, rect=(x1, y1, x2, y2),
        по умолчанию rect=(10, 10, 90, 90)
    :param kwargs: xlim, ylim (интервалы по осям x и y соотвественно), тип tuple; пример: xlim=(0,1), ylim=(1,2)
    :return:
    """
    string1 = "$!PLOTTYPE = CARTESIAN2D\n" \
              "$!TWODAXIS XDETAIL{VARNUM = %s}\n" \
              "$!TWODAXIS YDETAIL{VARNUM = %s}\n" \
              "$!TWODAXIS\n" \
              "  GRIDAREA\n" \
              "  {\n" \
              "    EXTENTS\n" \
              "    {\n" \
              "      X1 = %s\n" \
              "      Y1 = %s\n" \
              "      X2 = %s\n" \
              "      Y2 = %s\n" \
              "    }\n" \
              "  }\n" % (x_axis_var.value, y_axis_var.value, rect[0], rect[1], rect[2], rect[3])
    if 'xlim' in kwargs and 'ylim' in kwargs:
        string2 = "$!TWODAXIS\n" \
                  "  XDETAIL\n" \
                  "    {\n"\
                  "    RANGEMIN = %s\n" \
                  "    RANGEMAX = %s\n" \
                  "    }\n" \
                  "  YDETAIL\n" \
                  "    {\n" \
                  "    RANGEMIN = %s\n" \
                  "    RANGEMAX = %s\n" \
                  "    }\n" % (kwargs['xlim'][0], kwargs['xlim'][1], kwargs['ylim'][0], kwargs['ylim'][1])
    else:
        string2 = ''
    result = string1 + string2
    return result


def get_var_and_levels_setting_macro(variable_number: int, min_level, max_level,
                                     num_levels: int) -> str:
    levels = np.linspace(min_level, max_level, num_levels)
    result = "$!SETCONTOURVAR\n" \
             "  VAR = %s\n" \
             "  CONTOURGROUP = 1\n" \
             "$!CONTOURLEVELS NEW\n" \
             "  CONTOURGROUP = 1\n" \
             "  RAWDATA\n" \
             "%s\n" % (variable_number, len(levels))
    template = '%s\n'
    for i in levels:
        result += template % i
    return result


def get_legend_settings_macro(xy_position: tuple = (95, 80), rowspacing: float = 1.2, auto_levelskip: int = 1,
                              isvertical: bool = True) -> str:
    if isvertical:
        isvertical_str = 'YES'
    else:
        isvertical_str = 'NO'
    result = "$!GLOBALCONTOUR 1  LEGEND{ISVERTICAL = %s}\n" \
             "$!GLOBALCONTOUR 1  LABELS{AUTOLEVELSKIP = %s}\n" \
             "$!GLOBALCONTOUR 1  LEGEND{ROWSPACING = %s}\n" \
             "$!GLOBALCONTOUR 1\n" \
             "LEGEND\n" \
             "{\n" \
             "SHOW = YES\n" \
             "XYPOS\n" \
             "{\n" \
             "X = %s\n" \
             "Y = %s\n" \
             "}\n" \
             "}\n" % (isvertical_str, auto_levelskip, rowspacing, xy_position[0], xy_position[1])
    return result


class ColorDistribution(enum.Enum):
    BANDED = 0
    CONTINUOUS = 1


class ColorMap(enum.Enum):
    MODERN = "'Modern'"
    SMALL_RAINBOW = "'Small Rainbow'"
    WILD = "'Wild'"
    GRAY_SCALE = "GrayScale"


def get_colormap_settings_macro(color_distribution: ColorDistribution = ColorDistribution.BANDED,
                                colormap_name: ColorMap = ColorMap.MODERN, **kwargs) -> str:
    """
    :param color_distribution:
    :param colormap_name:
    :param kwargs: color_max и color_min, если распределение цвета =  ColorDistribution.CONTINUOUS
    :return:
    """
    string1 = "$!GLOBALCONTOUR 1  COLORMAPNAME = %s\n" \
              "$!GLOBALCONTOUR 1  COLORMAPFILTER{COLORMAPDISTRIBUTION = %s}\n" % (colormap_name.value,
                                                                                  color_distribution.name)
    if color_distribution == ColorDistribution.CONTINUOUS and 'color_min' in kwargs and 'color_max' in kwargs:
        string2 = "$!GLOBALCONTOUR 1  COLORMAPFILTER{CONTINUOUSCOLOR{CMIN = %s}}\n" \
                  "$!GLOBALCONTOUR 1  COLORMAPFILTER{CONTINUOUSCOLOR{CMAX = %s}}\n" % (kwargs['color_min'],
                                                                                       kwargs['color_max'])
    else:
        string2 = ''
    result = string1 + string2
    return result


def get_extract_slice_command() -> str:
    return "$!CREATESLICEZONES\n"


def get_activate_zones_command(zone_number_list: typing.List[int]) -> str:
    zones = ''
    for n, i in enumerate(zone_number_list):
        if n != len(zone_number_list) - 1:
            zones += '%s,' % i
        else:
            zones += '%s' % i
    result = "$!ACTIVEFIELDMAPS = [%s]\n" % zones
    return result


def get_export_command(exportfname, imagewidth=1200) -> str:
    result = "$!EXPORTSETUP EXPORTFNAME = '%s'\n" \
             "$!EXPORTSETUP IMAGEWIDTH = %s\n" \
             "$!EXPORT\n" \
             "  EXPORTREGION = CURRENTFRAME\n" % (exportfname, imagewidth)
    return result


def get_delete_zones_command(zone_number_list: typing.List[int]) -> str:
    zones = ''
    for n, i in enumerate(zone_number_list):
        if n != len(zone_number_list) - 1:
            zones += '%s,' % i
        else:
            zones += '%s' % i
    result = "$!DELETEZONES [%s]\n" % zones
    return result


def get_show_contour_command() -> str:
    return "$!FIELDLAYERS SHOWCONTOUR = YES\n"


def get_go_to_3d_command() -> str:
    return "$!PLOTTYPE = CARTESIAN3D\n"


def get_create_picture_macro(x_axis_var: Variable, y_axis_var: Variable, zone_number: int,
                             exportfname, rect: tuple = (10, 10, 90, 90), imagewidth=1200, **kwargs) -> str:
    """
    :param x_axis_var: величина по горизонтальной оси
    :param y_axis_var: величина по вертикальной оси
    :param zone_number: номер зоны, подлежащей активации и удалению
    :param rect: определяет положение прямоугольника сетки на frame, rect=(x1, y1, x2, y2),
        по умолчанию rect=(10, 10, 90, 90)
    :param exportfname: имя файла, в который будет осуществляться эскпорт
    :param imagewidth: ширина картинки
    :param kwargs: xlim и ylim (интервалы по осям x и y соотвественно), тип tuple; пример: xlim=(0,1), ylim=(1,2)
    :return: макрос, который извлекает данные из текущего среза, активирует отображение цвета, переходит в
        2d координаты, с заданными величинами по горизонтальной и вертикальной оси, активирует зону,
        осуществляет экспорт, удаляет зону и переходит обратно в 3d координаты
    """
    extract_slice = get_extract_slice_command()
    show_contour = get_show_contour_command()
    go_to_2d = get_go_to_2d_macro(x_axis_var, y_axis_var, rect, **kwargs)
    activate_zone = get_activate_zones_command([zone_number])
    export = get_export_command(exportfname, imagewidth)
    delete_zone = get_delete_zones_command([zone_number])
    go_to_3d = get_go_to_3d_command()
    result = extract_slice + show_contour + go_to_2d + activate_zone + export + delete_zone + go_to_3d
    return result


class SliceSettings:
    def __init__(self, slice_type: SliceType, position: tuple, **kwargs):
        """
        :param slice_type: определяет ориентацию секущей плоскости
        :param position: кортеж из трех элементов, определяющих координаты точки, черех которую 
            проходит секущая плоскость
        :param kwargs: 1. normal - кортеж, задающий координаты нормали к секущей плоскости, необходимо задать, если
                slice_type = SliceType.ARBITRARY
        """
        self.slice_type = slice_type
        self.position = position
        self.kwargs = kwargs


class LevelSettings:
    def __init__(self, variable_number: int, min_level, max_level, num_levels: int):
        """
        :param variable_number: номер отображаемой переменной переменной
        :param min_level: нижняя граница отображаемого интервала значений переменной
        :param max_level: верхняя граница отображаемого интервала значений переменной
        :param num_levels: число уровней в легенде
        """
        self.variable_number = variable_number
        self.min_level = min_level
        self.max_level = max_level
        self.num_levels = num_levels


class LegendSettings:
    def __init__(self, xy_position: tuple = (95, 80), rowspacing: float = 1.2, auto_levelskip: int = 1,
                 isvertical: bool = True):
        """
        :param xy_position: позиция легенды в координатах экрана, по умолчанию (95, 80)
        :param rowspacing: интервал между строками, по умолчанию 1.2
        :param auto_levelskip: пропуск уровней, по умолчанию 1 (без пропуска)
        :param isvertical: параметр, определяющей вертикальность легенды, по умолчанию True
        """
        self.xy_position = xy_position
        self.rowspacing = rowspacing
        self.auto_levelskip = auto_levelskip
        self.isvertical = isvertical


class ColormapSettings:
    def __init__(self, color_distribution: ColorDistribution = ColorDistribution.BANDED,
                 colormap_name: ColorMap = ColorMap.MODERN, **kwargs):
        """
        :param color_distribution: распределения цвета, по умолчанию ColorDistribution.BANDED
        :param colormap_name: цветовая схема, по умолчанию ColorMap.MODERN
        :param kwargs: color_max и color_min, если распределение цвета =  ColorDistribution.CONTINUOUS
        """
        self.color_distribution = color_distribution
        self.colormap_name = colormap_name
        self.kwargs = kwargs


class AxisSettings:
    def __init__(self, x_axis_var: Variable, y_axis_var: Variable, rect: tuple = (10, 10, 90, 90), **kwargs):
        """
        :param x_axis_var: переменная, откладываемая по горизонтальной оси, например, x_axis_var = Variable.X
        :param y_axis_var: переменная, откладываемая по вертикальной оси
        :param rect: определяет положение прямоугольника сетки на frame, rect=(x1, y1, x2, y2),
            по умолчанию rect=(10, 10, 90, 90)
        :param kwargs: xlim и ylim (интервалы по осям x и y соотвественно), тип tuple; пример: xlim=(0,1), ylim=(1,2)
        """
        self.x_axis_var = x_axis_var
        self.y_axis_var = y_axis_var
        self.rect = rect
        self.kwargs = kwargs


class ExportSettings:
    def __init__(self, zone_number: int, exportfname, imagewidth=1200):
        """
        :param zone_number: номер зоны, в которую будут извлечены данные среза, (на единицу большего общего
            количества зон)
        :param exportfname:  имя файла, в который будет осуществляться экспорт
        :param imagewidth: ширина картинки
        """
        self.zone_number = zone_number
        self.exportfname = exportfname
        self.imagewidth = imagewidth


class PictureCreator:
    def __init__(self, data_filename, macro_filename, slice_settings: SliceSettings, level_settings: LevelSettings,
                 legend_settings: LegendSettings, colormap_settings: ColormapSettings,
                 axis_settings: AxisSettings, export_settings: ExportSettings):
        self.data_filename = data_filename
        self.macro_filename = macro_filename
        self.slice_settings = slice_settings
        self.level_settings = level_settings
        self.legend_settings = legend_settings
        self.colormap_settings = colormap_settings
        self.axis_settings = axis_settings
        self.export_settings = export_settings

    def _get_slice_settings_macro(self) -> str:
        return get_slice_setting_macro(self.slice_settings.slice_type, self.slice_settings.position,
                                       **self.slice_settings.kwargs)

    def _get_level_settings_macro(self) -> str:
        return get_var_and_levels_setting_macro(self.level_settings.variable_number, self.level_settings.min_level,
                                                self.level_settings.max_level, self.level_settings.num_levels)

    def _get_legend_settings_macro(self) -> str:
        return get_legend_settings_macro(self.legend_settings.xy_position, self.legend_settings.rowspacing,
                                         self.legend_settings.auto_levelskip, self.legend_settings.isvertical)

    def _get_colormap_settings_macro(self) -> str:
        return get_colormap_settings_macro(self.colormap_settings.color_distribution,
                                           self.colormap_settings.colormap_name, **self.colormap_settings.kwargs)

    def _get_create_picture_macro(self):
        return get_create_picture_macro(self.axis_settings.x_axis_var,
                                        self.axis_settings.y_axis_var,
                                        self.export_settings.zone_number,
                                        self.export_settings.exportfname,
                                        self.axis_settings.rect,
                                        self.export_settings.imagewidth, **self.axis_settings.kwargs)

    def run_creation(self):
        open_file = get_open_data_file_command(self.data_filename)
        slice_settings = self._get_slice_settings_macro()
        level_settings = self._get_level_settings_macro()
        legend_settings = self._get_legend_settings_macro()
        colormap_settings = self._get_colormap_settings_macro()
        create_picture = self._get_create_picture_macro()
        macro = wrap_macro(open_file + slice_settings + level_settings + legend_settings + colormap_settings +
                           create_picture)
        create_macro_file(macro, self.macro_filename)
        execute_macro(self.macro_filename)


if __name__ == '__main__':
    slice_settings = SliceSettings(SliceType.ARBITRARY, (0.1, 0.15, 0.1), normal=(0, 1, 0))
    legend_settings = LegendSettings(xy_position=(90, 45))
    levels_settings = LevelSettings(5, 0, 90, 10)
    colormap_settings = ColormapSettings(ColorDistribution.BANDED, ColorMap.MODERN)
    axis_settings = AxisSettings(Variable.X, Variable.Z, rect=(10, 10, 80, 40),
                                 xlim=(-0.1, 8.1), ylim=(-0.05, 0.4))
    export_settings = ExportSettings(2, r'pictures\test.png')
    pic_creator = PictureCreator(r'data_files\average_grid_density_sp_al.plt', 'macros\picture_creation.mcr',
                                 slice_settings, levels_settings, legend_settings, colormap_settings,
                                 axis_settings, export_settings)
    pic_creator.run_creation()
