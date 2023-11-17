from processing_algorithm import ProcessingAlgorithm
from qgis.core import QgsProcessingProvider


class Provider(QgsProcessingProvider):
    def __init__(self) -> None:
        super().__init__()

        self._id = "myprovider"
        self._name = "My provider"

    def id(self) -> str:
        """The ID of your plugin, used to identify the provider.

        This string should be a unique, short, character only string,
        eg "qgis" or "gdal". This string should not be localised.
        """
        return self._id

    def name(self) -> str:
        """
        The display name of your plugin in Processing.

        This string should be as short as possible and localised.
        """
        return self._name

    def load(self) -> bool:
        self.refreshAlgorithms()
        return True

    def icon(self):
        """
        Returns a QIcon which is used for your provider inside the Processing toolbox.
        """
        return QgsProcessingProvider.icon(self)

    def loadAlgorithms(self) -> None:
        """
        Adds individual processing algorithms to the provider.
        """
        alg = ProcessingAlgorithm()
        self.addAlgorithm(alg)
