from src.views.statistics import StatisticsView


class StatisticsWriteView(StatisticsView):
    def __setup_io__(self):
        raise NotImplementedError()

    def __setup_and_read_from_cache__(self):
        self.__setup_io__()
        self.io.read_from_disk()
