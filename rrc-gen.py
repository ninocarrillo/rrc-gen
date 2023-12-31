'''
MIT License

Copyright (c) 2023 Nino Carrillo KK4HEJ

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import os
import sys
import math
import numpy as np
import matplotlib.pyplot as plt

def InitRRCFilter(this):
	this['TapCount'] = int(math.ceil(this['symbol span'] * this['samples per symbol'])) + 1
	this['TimeStep'] = 1 / this['samples per symbol']
	this['SymbolTime'] = 1
	this['Time'] = np.arange(0, this['TapCount'] * this['TimeStep'], this['TimeStep']) - (this['TapCount'] * this['TimeStep'] / 2) + (this['TimeStep'] / 2)
	this['XTicks'] = np.arange(-math.ceil(this['symbol span'] / 2), math.ceil(this['symbol span'] / 2) + 1)
	this['Taps'] = np.zeros(this['TapCount'])
	index = 0
	try:
		asymptote = this['SymbolTime'] / (4 * this['rolloff rate'])
	except:
		asymptote = False
	for time in this['Time']:
		if math.isclose(time,-asymptote) or math.isclose(time, asymptote):
			numerator = this['rolloff rate'] * ((1 + 2 / np.pi) * np.sin(np.pi/(4 * this['rolloff rate'])) + (1 - (2 / np.pi)) * np.cos(np.pi / (4 * this['rolloff rate'])))
			denominator = this['SymbolTime'] * pow(2, 0.5)
			this['Taps'][index] = numerator / denominator
		elif math.isclose(time, 0):
			numerator = 1 + (this['rolloff rate'] * ((4 / np.pi) - 1))
			denominator = this['SymbolTime']
			this['Taps'][index] = numerator / denominator
		else:
			numerator = np.sin(np.pi * time * (1 - this['rolloff rate']) / this['SymbolTime']) + 4 * this['rolloff rate'] * time * np.cos(np.pi * time * (1 + this['rolloff rate']) / this['SymbolTime']) / this['SymbolTime']
			denominator = np.pi * time * (1 - pow(4 * this['rolloff rate'] * time / this['SymbolTime'], 2)) / this['SymbolTime']
			try:
				this['Taps'][index] = numerator / (denominator * this['SymbolTime'])
			except:
				pass
		index += 1
	this['Taps'] = this['Taps'] / np.linalg.norm(this['Taps'])
	this['RC'] = np.convolve(this['Taps'], this['Taps'], 'same')
	return this
	
def GenInt16ArrayC(name, array, column_width):
	result = '\n'
	result += f'const __prog__ int16_t __attribute__((space(prog))) {name}[{len(array)}] = '
	result += '{ '
	y = len(array)
	for x in range(y):
		if x % column_width == 0:
			result += ' \\\n     '
		result += f' {int(np.rint(array[x]))}'
		if x < (y-1):
			result += ','
	result += ' };'
	return result

if len(sys.argv) < 5:
		print("Not enough arguments. Usage: python3 rrc-gen.py <rolloff rate> <span> <samples per symbol> <amplitude>")
		sys.exit(-1)

filter = {}
filter['rolloff rate'] = float(sys.argv[1])
filter['symbol span'] = int(sys.argv[2])
filter['samples per symbol'] = int(sys.argv[3])
filter['amplitude'] = int(sys.argv[4])

filter = InitRRCFilter(filter)
filter['ScaledTaps'] = np.rint(filter['Taps'] * filter['amplitude'])
filter['ScaledRC'] = np.rint(filter['RC'] * filter['amplitude'])

plt.figure()
plt.plot(filter['Time'],filter['ScaledTaps'])
plt.plot(filter['Time'],filter['ScaledRC'])
plt.xticks(filter['XTicks'])
plt.title(f'Raised Cosine Rolloff: {filter["rolloff rate"]}')
plt.legend(['RRC', 'RC'])
plt.grid()
plt.show()

#generate a new director for the reports
run_number = 0
print('trying to make a new directory')
while True:
	run_number = run_number + 1
	dirname = f'./run{run_number}/'
	try:
		os.mkdir(dirname)
	except:
		print(dirname + ' exists')
		continue
	print(f'made new directory {dirname}')
	break

# Generate and save report file
report_file_name = f'run{run_number}_report.txt'
try:
	report_file = open(dirname + report_file_name, 'w+')
except:
	print('Unable to create report file.')
with report_file:
	report_file.write('# Command line: ')
	for argument in sys.argv:
		report_file.write(f'{argument} ')

	report_file.write('\n\n# RRC Pulse Filter\n')
	report_file.write('\n')
	report_file.write(GenInt16ArrayC(f'RRCFilter', filter['ScaledTaps'], filter['samples per symbol']))
	report_file.write('\n')
	report_file.close()
	print(f'wrote {dirname + report_file_name}')
