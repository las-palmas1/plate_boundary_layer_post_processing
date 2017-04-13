from tecplot_lib import PolyLine, Point, LineDataExtractor

pln_set1 = [PolyLine([Point(7.9, 0.15, 0), Point(7.9, 0.15, 0.35)], 1500),
            PolyLine([Point(7.9, 0.15, 0), Point(7.9, 0.15, 0.003)], 3000),
            PolyLine([Point(0, 0.15, 0), Point(8, 0.15, 0)], 2000)]
ace_data_files_dir = r'data_files\ace'
ace_extracted_data_dir = r'extracted_data\ace'

cfx_data_files_dir = r'data_files\cfx'
cfx_extracted_data_dir = r'extracted_data\cfx'

ace_extractor = LineDataExtractor(ace_data_files_dir, ace_extracted_data_dir, [pln_set1, pln_set1, pln_set1,
                                                                               pln_set1, pln_set1, pln_set1,
                                                                               pln_set1, pln_set1, pln_set1],
                                  r'macros\ace_data_extraction.mcr')

cfx_extractor = LineDataExtractor(cfx_data_files_dir, cfx_extracted_data_dir, [pln_set1],
                                  r'macros\cfx_data_extraction.mcr')

if __name__ == '__main__':
    ace_extractor.run_extraction()
    cfx_extractor.run_extraction()
