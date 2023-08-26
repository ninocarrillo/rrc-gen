# rrc-gen
Generate finite impulse response taps for square root raised cosine filters, using design parameters passed on the command line. The program generates a plot of the Raised Cosine and Root Raised Cosine impulse response for the arguments passed, and generates a report file that contains a c-style array of filter taps.
## Requires
- Python3
- NumPY
## Usage
````
python3 rrc-gen.py <rolloff rate> <span> <samples per symbol> <amplitude>
```` 
## Example
````
python3 rrc-gen.py 0.2 8 6 25000
````
![image](./RRC02.png)
