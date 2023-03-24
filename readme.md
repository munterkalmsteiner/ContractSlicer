# Step 1: Create query
We need to create a query image that serves as input for the comparison.

## Step 1.1:
pdftoppm -png -f $PAGE -l $PAGE -rx 200 -ry 200 $FILENAME.pdf > $PAGE.png

## Step 1.2:
Use a screenshot tool to create a screenshot of the query from $PAGE.png. Make sure to view the image at 100% scale when taking the screenshot.
We are interested in the height of the query as we need that as input parameter for the query_creator

## Step 1.3:
python ./query_creator.py avtal/$FILENAME.pdf $PAGE $HEIGHT queries/

## Step 1.4:
Find the query file in the folder queries/$FILENAME/$PAGE and copy it to queries

# Step 2: run slicer
python ./slicer.py queries/ avtal/ results/


