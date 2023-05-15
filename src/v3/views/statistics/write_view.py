from src.v3.views.statistics import StatisticsView


class StatisticsWriteView(StatisticsView):
    def __setup_io__(self):
        raise NotImplementedError()

    def __handle_valid_job__(self):
        raise NotImplementedError()

    def __read_from_cache__(self):
        self.__setup_io__()
        self.io.read_from_disk()
