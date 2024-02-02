# Process

## Step 1: Record Creation

- Input
    - AIS data (ship records)
    - output directory (path to store tfrecords)
    - sample rate
    - detect range
    - buffer range
    - sensor location
    - start time, end time
    - mmsi information (scraped)
    - wav directory (audio data)
    - segment length seconds (30 second default)
    - type (mars or harp)

Process begins with supplying a time range to develop samples for. 
Given the information that is present in the AIS data as well as the scraped mmsi information, we can then formulate trip information (speed, location, time, identification number).

Audio Fetcher is then created to grab the audio for the specified amount of time. This is then carved into segments of specified length (segment length seconds) and returned to the user where they will be individually labeled. 

For each segment of time, the following process is used to label the segment

    - From AIS data, filter all trips and limit to the segment of time (start time nanos, end time nanos) and categorize into ships that are in the detect zone and buffer zone
    - If there are any ships in the buffer zone for the segment of time, the segment is not labeled and is skipped
    - For every ship in the detect zone, information about the ships (bearing, range, mmsi, and description) are assigned a label based on the class of ship that is being identified. A list of these classifications can be found in constants.py. 
    - Using the label information above results in the creation of a single tfrecord, denoted by the format:
    
        "{start_time_nanos}_{end_time_nanos}_{A}_{B}_{C}_{D}_{E}_{F}.tfrecord"

    where (A, B, C, D, E, F) all indicate the presence of a certain class of ship. F Class indicates that there is no ship present and no other flags in the label should be on.

Once all the records have been created for a specified detect/buffer range, a look-up table is created for the specific directory of tfrecords. It is organized as pairs of intervals and labels, matching the naming convention of the record files.

## Step 2: Splits Creation

We can create our training splits based on specified periods of time. Once we have the associated records and our look up table, we can use the query functionality to gather records based on time. An example of this can be as follows:

Train: 02/2019 - 06/2021
Validation: 06/2021 - 09/2021
Test: 09/2021 - 12/2021

Splits can be created in many different ways, with different combination of times (weeks of the month, certain days, etc.) utilizing the existing system.

Once certain splits are created, we can modify the splits for training efficiency, randomizing and grouping samples together rather than keeping each sample per tfrecord. 

## Step 3: Training



