## GDC submitter translation UI

This application is to help submitter create YAML and CONF input files for the [GDC submitter](https://github.com/NCI-GDC/gdc-submitter).

### Installation

We suggest to work in the python virtual environment.
- Download source code:
  `git clone git@github.com:NCI-GDC/gdc_submitter_translation_ui.git`
- Install dependencies:
  `python setup.py install`
- Run the app:
  `python submitter_ui/app.py`
- Open a web browser, and go to `localhost:5000/`

### More about the UI
The YAML and CONF files created here are for the [GDC submitter](https://github.com/NCI-GDC/gdc-submitter) only. If you desired to submit through API, please refer to [GDC doc site](https://docs.gdc.cancer.gov/API/Users_Guide/Submission/).

The YAML tells the GDC submitter which properties it should be looking for and where it could be found in your uploaded TSV file.
- For required properties, there is no way to deselect. However, they do not have to be in the TSV, since many of them could be just selected from `enum`.
- For optional properties, not including `links`, submitter is able to deselect the node by delete button. Unfortunately, the current UI does not have a undo or restore function. If submitter accidentally deletes a desired node, one has to refresh the page. :(
- `s3_loc` is not a property in the API, but in the GDC submitter. It exists in all the node in this UI, please feel free to delete it if you do not need.
- For properties that are also `links`, they would not be presented in the YAML output, but in CONF. Please see more details below.

The CONF tells the GDC submitter what is the link/anchor node and where it is in the TSV.
- The current design of the GDC submitter only supports **ONE** link/anchor node in the CONF. However, the current UI is able to present all the links that submitter selects in the CONF which will unfortunately crash the GDC submitter. A better designed UI would then have to create multiple YAMLs based on selected links in order to cooperate, which will be happening soon.
- Because of the above issue, submitter now has to be responsible to select only one link/anchor node, and delete others.
- The `link_id_type` is basically telling the GDC submitter which id you are using in your TSV. It's either `id` or `submitter_id`.
- If submitter is going to perform a replacement upon the submission, one has to create a `to_be_deleted.yaml` by selecting the checkbox. It will then popup 2 new fields which will be in the final output, and provides the info that the GDC submitter needs.
