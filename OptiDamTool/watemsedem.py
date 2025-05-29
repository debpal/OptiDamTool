class WatemSedem:

    '''
    Provides functionality to prepare the necessary inputs
    for simulating the `WaTEM/SEDEM <https://github.com/watem-sedem>`_ model.
    '''

    def dem_to_stream(
        self,
        dem_file: str,
        folder_path: str
    ) -> list[str]:

        '''
        Generates `stream files <https://watem-sedem.github.io/watem-sedem/input.html>`_  
        required to run the WaTEM/SEDEM model with the extension  
        **output per river segment = 1**.

        Parameters
        ----------
        dem_file : str
            Path to the input DEM file.

        folder_path : str
            Path to the output folder.

        Returns
        -------
        list
            A list containing confirmation messages.
        '''

        output = [dem_file, folder_path]

        return output
