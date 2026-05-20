# EMC Repository Template

Getting all the right files in the right place can be a pain. 
This is a simple template repository that you can use to ensure you have all the right files present in your repo.

## Files you need

These should be at the top level of your repository:

* `README.md` - The `README.md` file should have a short section at the bottom
  called "DISCLAIMER", with a really brief statement saying that code is provided on an "as is" basis, and the user assumes responsibility for its use.
* `LICENSE` - The text of the `CC0` license.
* `DISCLAIMER` - Disclaimer 
   
## License

This project is part of NOAA-EMC Ecosystem. 

See LICENSE and DISCLAIMER for details.

## Radiosonde latency plotting

Use `plot_radiosonde_latency.py` to plot the latency between radiosonde report
valid time and BUFR tank receipt time (from `rtrcpt` in `nceplibs-bufr`):

```bash
python plot_radiosonde_latency.py /path/to/input.bufr --message-type-filter ADPUPA --cutoff-minutes 180
```
