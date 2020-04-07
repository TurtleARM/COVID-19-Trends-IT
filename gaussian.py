import numpy as np
from classes.CSV_parser import CSV_parser
from classes.github_downloader import github_downloader
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons
from scipy.optimize import curve_fit
import colorsys
import math 

doNotDownload = False

# Define a gaussian function
def gaussian_func(x, a, mu, sigma):
    return a * np.exp(-(x-mu)**2/(2*sigma**2))

regioni = {}

if not doNotDownload:
    # Gestione dati regioni in un file CSV
    filesToDownload = ["https://api.github.com/repos/pcm-dpc/COVID-19/contents/dati-regioni/dpc-covid19-ita-regioni.csv",
                       "https://api.github.com/repos/pcm-dpc/COVID-19/contents/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv"]
    downloader = github_downloader(filesToDownload)
    downloadedFiles = downloader.downloadFiles()
    with open("resources/regioni.csv", "w") as f:
        decodedFileRegioni = downloadedFiles[0].decode('utf-8')  # convert from bytearray
        f.write(decodedFileRegioni)
    with open("resources/italia.csv", "w") as f:
        decodedFileNazione = downloadedFiles[1].decode('utf-8')
        f.write(decodedFileNazione)

fileRegioni = CSV_parser("resources/regioni.csv")
fileNazione = CSV_parser("resources/italia.csv")
fileRegioniList, fileNazioneStr = fileRegioni.parseFileRegioni(), fileNazione.parseFileNazione()

# Parsing regioni singole
POS_NOME = fileRegioni.getTitles().index("denominazione_regione")
POS_POSITIVI = fileRegioni.getTitles().index("nuovi_positivi")
POS_NUOVI_POSITIVI = fileNazione.getTitles().index("nuovi_positivi")

# Inizializza chiavi regioni e aggiungi 
for line in fileRegioniList:
    nomeRegione = line.split(",")[POS_NOME]
    if nomeRegione not in regioni:
        regioni[nomeRegione] = []
    regioni[nomeRegione].append(line)
    
with open('resources/lombardia.csv', 'w') as f:
    f.writelines("%s\n" % line for line in regioni["Lombardia"])

# Gestione dati nazionali
nuoviContagiItalia = []
for line in fileNazioneStr.splitlines():
    nuoviContagiItalia.append(int(line.split(',')[POS_NUOVI_POSITIVI]))
giorni = len(nuoviContagiItalia)
x = range(giorni)
poptIt, pcovIt = curve_fit(gaussian_func, x, nuoviContagiItalia)

# Gestione dati regionali
nuoviContagiRegione = {}
for regione in regioni: 
    for line in regioni[regione]:
        if regione not in nuoviContagiRegione:
            nuoviContagiRegione[regione] = []
        nuoviContagiRegione[regione].append(line.split(',')[POS_POSITIVI])

popt, pcov = [None]*len(nuoviContagiRegione), [None]*len(nuoviContagiRegione)

i = 0
for contagiRegione in nuoviContagiRegione:
    popt[i], pcov[i] = curve_fit(gaussian_func, x, nuoviContagiRegione[contagiRegione])
    i += 1
    
# Report
MSE = 0
for giorno in x:
    MSE += math.pow(gaussian_func(giorno, *poptIt) - nuoviContagiItalia[giorno], 2)
MSE = MSE / giorni
RMSE = math.sqrt(MSE)

xplot = np.linspace(0, 90, 500)

print("Expected number of new cases: ", gaussian_func(giorni - 1, *poptIt),
      "\nActual number of new cases: ", nuoviContagiItalia[giorni - 1])
print("Tomorrow's expected number of new cases: ", gaussian_func(giorni, *poptIt))
print("R(t) =", gaussian_func(giorni - 1, *poptIt)/gaussian_func(giorni - 2, *poptIt), "over daily cycles")

smallest = 0
for i in xplot:
    if gaussian_func(i, *poptIt) > 0.8 and gaussian_func(i, *poptIt) < 1.2:
        smallest = i

print("There will be", gaussian_func(smallest, *poptIt), "cases on day", smallest)
print("Model Relative Mean Squared Error:", RMSE)
# Show charts

# Setup RGB colors
N = len(regioni)
HSV_tuples = [(x*1.0/N, 0.5, 0.5) for x in range(N)]
RGB_tuples = list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples))

# Generate subplots
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.45, bottom=0.1, right=0.96, top=0.95)
fig = plt.gcf()
fig.set_size_inches(12.5, 8.5, forward=True)
plt.xticks([0, 10, 20, 30, 40, 52, 60, 70, 80], ['24/2', '3/3', '12/3', '22/3', '1/4', '13/4', '22/4', '2/5', '12/5']) # pls automate me :'(

charts = []
i = 0
for regione in regioni:
    chartRegione, = ax.plot(xplot, gaussian_func(xplot,*popt[i]), visible=False, lw=2, color=RGB_tuples[i], label=regione)
    charts.append(chartRegione)
    i+=1

# Set default visible charts #####
labels = [str(chart.get_label()) for chart in charts]
index = labels.index("Lombardia")
charts[index].set_visible(True)
##################################

visibility = [chart.get_visible() for chart in charts]
chartItalia, = ax.plot(xplot, gaussian_func(xplot,*poptIt), visible=True, lw=2, color='b', label='Italia')
ax.scatter(x, nuoviContagiItalia)
charts.append(chartItalia)

rax = plt.axes([0.01, 0.15, 0.34, 0.75])
check = CheckButtons(rax, labels, visibility)

def func(label):
    index = labels.index(label)
    charts[index].set_visible(not charts[index].get_visible())
    plt.draw()

check.on_clicked(func)

plt.show()
