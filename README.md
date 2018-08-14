# con-text-ver-2
This is version 2 of con-text, a book ranking system, that reads book reviews from the internet and extracts a qualitative maesure for the books based on a set of categories.
## How to run
### Webcrawling
Firstly the database needs to be set up. For this project we used Firebase. The database is built using the webcrawler stored in the subdirectory Honey. It was written using scrapy. 
--The webcrawler is currently under construction---
### Datapipeline
After the database is built up run the main to extract info from the database:
```
python main.py 0
```
Then the word biases are calculated:
```
python main.py 1
```
Lastly preparations for the GloVe algorithm are made (the c code in Pre_Post_Processing/src must be compiled and the executable files stored in Pre_Post_Processing/build) : 
```
python main.py 2
gcc -o cooccur.c cooccur
gcc -o glove.c glove
gcc -o shuffle.c shuffle
gcc -o vocab_count.c vocab_count
```
Then the GloVe algorithm is executed (note the comments at the top of demo.sh if you are running on Mac OS):
```
./demo.sh
```
The final results are obtained with the following shell script (this script employs the Stanford Parser and it must be downloaded from the website):
```
./batch_score_calc.sh
```
Your results can now be viewed in the database. To touch up the results by performing adaptive histogram equalization and to get .csv plots of your results and performance run these commands:
```
python adaptive_hist_eq.py
python testing.py
```
