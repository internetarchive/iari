from src.views.statistics import StatisticsView


class StatisticsWriteViewV2(StatisticsView):
    def __setup_io__(self):
        raise NotImplementedError()

    def __setup_and_read_from_cache__(self):
        self.__setup_io__()  # sets up "io" property as FileIo instance
        self.io.read_from_disk()
