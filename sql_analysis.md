# OpenStreetMap Data - Munich

### Map source and info

For this project I decided to have a look at Munich/Germany, because it is where I live and is also a quite popular city arround the world. The OpenStreetMap OSM data was downloaded via the MAPZEN service:

https://mapzen.com/data/metro-extracts/metro/munich_germany/

## Data cleaning

### Used scripts

- explore.py => explore data and find problems
- check_correct.py
- cleaning.py => main script and import

### Data analysis and cleaning

To explore the data and find possible issues, I create a 'explore.py' script. 
It allows me to have a look into the ways, nodes and tags and select individual 
areas for further analysis.

The script takes two arguments: the name of the OSM file and the type of tags 
that shall be analysed ('way' or 'tag'). After reading the data, it lists the 
most common tag types. This is helpful as an overview for further exploring.

Also, there is an overview of the top 10 tag types and their most common values.

After this general information, there is a prompt that asks for a tag type. This
allows to list all values of a tag type, ordered by number of occurences.

The script can be used to find problems in the data. For example if we enter 'addr:city',
we can finde some wrong values - e.g. 'MÜ', 'Müchen', 'Muchen', etc. While these 
kind of problems can not be spotted programatically, we create a text file with all 
the misspelled Names of 'Munich'. We later use this file to recognize bad values 
and substitute it by the correct one.

Looking at the city names ('addr:city') we see that there are different speelings 
for the same cities. We correct this by creating a mapping file called 'city-names.txt'. 
This includes the doublicat/wrong value and maps it to the correct value.

A last mapping file is created for the street names ('addr:street'). First we find 
typos programatically and then map these wrong values to the right ones. We save the 
mapping as 'stree-names.txt'.

More details about the encountered problems and their handling can be found in 'findings.txt'.

The functions for spotting problamatic data and correcting it, is included in the 
'check_and_correct.py' script. This is then used by the major 'cleaning.py' script 
that walks through the OSM data, corrects it if necessary and exports everything 
to csv files.

Finally, the csv files are importet into an sqlite database called '**TBD***'.

## General statistics

### File sizes
```
munich_germany.osm      486 MB
**DBFILE**              274 MB
nodes_tags.csv          29 MB
nodes.csv               153 MB
ways_tags.csv           41 MB
ways_nodes.csv          59 MB
ways.csv                21 MB
```


### Number of nodes

```
sqlite> SELECT count() FROM nodes;
```
1922928   

### Number of ways
```
sqlite> SELECT count() FROM ways;
```
380416

### Number of unique users
Let's first have a look how many users there are in each of the 'nodes' and \
'ways:

```sql
sqlite> SELECT count() 
FROM 
    (SELECT * FROM nodes GROUP BY user);
```
2675

```sql
sqlite> SELECT count() 
FROM 
    (SELECT * FROM ways GROUP BY user);
```
2058 

Now we want to combine the two user columns from each table and count the \
total number of unique users:

```sql
sqlite> SELECT count() 
FROM 
    (
    SELECT * 
    FROM 
        (
        SELECT user 
        FROM nodes 
        UNION all
        SELECT user 
        FROM ways
        )
    GROUP BY user
    ) 
;
```
3121


###  Most attributing users

```sql
sqlite> SELECT user, count()
FROM
     (
     SELECT user
     FROM nodes
     UNION ALL
     SELECT user 
     FROM ways
     )
 GROUP BY user    
 ORDER BY count() DESC
 LIMIT 20                                                          
 ;
 ```

```sql
user        count()   
----------  ----------
ToniE       256566    
rolandg     199541    
BeKri       183553    
heilbron    122617    
KonB        120266    
Basstoelpe  70773     
marek klec  59839     
osmkurt     49277     
zarl        43253     
why_not_zo  40894     
Filius Mar  39739     
ludwich     35074     
mawi42      34376     
q_un_go     33555     
shorty_de   31489     
burt13de    28865     
KPG         27776     
Anoniman    26360     
ms2000      25972     
Maturi0n    25530  
```


## Tags

### Top tag types
To further analyse the nodes and tags, we want to konw which types of tags \
are available:

```sql
sqlite> SELECT key, COUNT() as num
FROM nodes_tags
GROUP BY key
ORDER BY num DESC
LIMIT 50;
```

```sql
key                   num       
--------------------  ----------
street                128887    
housenumber           128488    
city                  98587     
postcode              92773     
country               86173     
name                  22597     
amenity               20219     
natural               19695     
entrance              18843     
highway               12411     
wheelchair            10424     
ref                   8476      
type                  7310      
source                7221      
shop                  7038      
barrier               6946      
level                 6747      
operator              6293      
website               5646      
emergency             5362      
phone                 5115      
railway               4778      
opening_hours         4756      
position              4453      
diameter              4426      
crossing              4417      
public_transport      4274      
leaf_type             3912      
denotation            3636      
bus                   3485      
bicycle               3419      
description           3248      
created_by            2873      
note                  2535      
power                 2331      
foot                  2123      
cuisine               1987      
information           1912      
access                1801      
vending               1718      
network               1709      
crossing_ref          1585      
email                 1582      
tourism               1459      
backrest              1441      
leisure               1344      
place                 1263      
capacity              1177      
fax                   1140      
material              1016  
```


### Number of amenities

```sql
sqlite>SELECT value, count() 
FROM nodes_tags 
WHERE key="amenity" 
GROUP BY value 
ORDER BY COUNT() desc 
LIMIT 10;
```

```sql
value       count()   
----------  ----------
bench       4301      
restaurant  1900      
vending_ma  1741      
recycling   1197      
bicycle_pa  951       
post_box    913       
waste_bask  851       
telephone   741       
cafe        694       
parking_en  640 
```

### Cafes with info
Let's create a more informative query. We want to get all cafes with their \
name and latitude/longitude:

```sql
SELECT nodes.id,lat,lon,names.value 
FROM 
    (select * from nodes_tags 
    WHERE key="amenity" and value="cafe") as cafes, 
    (select * from nodes_tags where key="name") as names, 
    nodes 
WHERE 
    cafes.id=nodes.id 
    AND names.id=cafes.id;

```sql
id          lat         lon         name         
----------  ----------  ----------  -------------
661339      48.1040226  11.4882626  Cafe Jeanette
82504563    48.2191919  11.675407   Cafe Waldeck 
185543052   48.2290815  11.671399   Riedmair     
185598892   48.220168   11.6739602  Dolomiti, Eis
185598916   48.2249115  11.6732913  Rick's Cafe  
196212074   48.1319808  11.5881662  Cafe Restaura
219688132   48.1498914  11.560239   Happy Fildjan
238410507   48.1819043  11.5725685  Pichler's Bac
239974120   48.1862375  11.5730045  Vinzenzmurr  
243693395   48.0644725  11.663411   Battke       
243858057   48.1501347  11.5598479  Cafe Havanna 
244015496   48.1509021  11.5653552  Joon         
244038472   48.1494922  11.5616482  Campanula
...
```
(resulting table shortened for presentation puproses)

### Most popular cuisines
Having a look at the 'keys' in 'nodes_tags', we can spot 'cuisine'. With \
this we can find out the most popular cuisines in the city:

```sql
sqlite>SELECT value, count() as num
FROM nodes_tags
WHERE key="cuisine"
GROUP BY value
ORDER BY num DESC
LIMIT 20;
```

```sql
value                 num       
--------------------  ----------
italian               417       
regional              147       
asian                 107       
greek                 106       
kebab                 102       
pizza                 96        
bavarian              86        
burger                70        
indian                69        
vietnamese            65        
international         52        
chinese               47        
german                43        
turkish               41        
ice_cream             39        
thai                  38        
coffee_shop           37        
japanese              36        
sushi                 26        
mexican               22 
```

### Leisure nodes
Another interesting tag is 'leisure'. Here is an overview of the top 20 \
values of that key:

```sql
sqlite>SELECT value, count() as num 
FROM nodes_tags 
WHERE key="leisure" 
GROUP BY value 
ORDER BY num DESC 
LIMIT 20;
```

```sql
value                 num       
--------------------  ----------
playground            939       
pitch                 142       
sports_centre         117       
fitness_station       33        
garden                23        
picnic_table          16        
tanning_salon         13        
fitness_centre        10        
adult_gaming_centre   6         
dance                 6         
sauna                 5         
swimming_pool         5         
bowling_alley         4         
music_venue           4         
hackerspace           3         
swimming_area         3         
water_park            3         
common                2         
dancing;music_venue   1         
dog_park              1 
```

## Ways

### Top tag types - ways

```sql
sqlite> SELECT key, COUNT() as num
FROM ways_tags
GROUP BY key
ORDER BY num DESC
LIMIT 50;
```

```sql
key                   num       
--------------------  ----------
building              219404    
highway               114062    
street                79280     
housenumber           77596     
city                  64975     
postcode              61526     
country               53514     
source                44237     
name                  38375     
shape                 36875     
levels                35405     
colour                31838     
surface               30562     
bicycle               24401     
maxspeed              21669     
foot                  17405     
service               16750     
access                12196     
smoothness            11488     
oneway                11485     
lanes                 9646      
layer                 9378      
amenity               9008      
landuse               8969      
lit                   8284      
level                 7547      
barrier               7193      
tunnel                7154      
ref                   6259      
height                5642      
indoor                5384      
leisure               5014      
tmc                   4904      
railway               4821      
segregated            4598      
wheelchair            4317      
orientation           4107      
gauge                 4106      
area                  3950      
note                  3524      
tracktype             3453      
incline               3402      
natural               3071      
electrified           2957      
voltage               2914      
operator              2813      
frequency             2800      
public_transport      2568      
cycleway              2536      
parking               2508 
```

### Speed limits

```sql
sqlite> SELECT value, COUNT() AS num
from ways_tags
WHERE key="maxspeed"
GROUP BY value
ORDER BY num DESC
LIMIT 10;
```

```sql
value                 num       
--------------------  ----------
30                    9541      
50                    7228      
60                    973       
DE:zone:30            525       
sign                  459       
DE:urban              374       
signals               285       
80                    267       
10                    255       
70                    253 
```

While there are some strange values, we can clearly see that the most common \
speed limit is 30 km/h followed by 50 km/h.


### Natural ways

```sql
sqlite> SELECT value, COUNT() AS num
from ways_tags
WHERE key="natural"
GROUP BY value
ORDER BY num DESC
LIMIT 10;
```

```sql
value                 num       
--------------------  ----------
tree_row              1051      
scrub                 699       
water                 634       
wood                  400       
grassland             172       
wetland               30        
shingle               23        
scree                 17        
heath                 14        
sand                  9  
```

## Further ideas
We could combine the position of cafes with position of trees (node type \
'natural'). This way we could find out which cafes are embadded in the \
greenest area. An idea would be to plot the cafe positions on a map \
and use the number of trees in a defined radius as a circle size. The cafes \
with the most trees arround them, would have big green circles.

### Possible problems
Probably not every tree is marked with a node. It is likely that clusters of \
trees are marked by only one node. This could distort the outcome.

Also, what if there are areas, where more trees are marked than in others?
