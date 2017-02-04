# OpenStreetMap Data - Munich

### Map source and info

For this project I decided to have a look at Munich/Germany, because it is where I live and is also a quite popular city around the world. The OpenStreetMap OSM data was downloaded via the MAPZEN service:

https://mapzen.com/data/metro-extracts/metro/munich_germany/

## Data cleaning

### Used scripts

- **util.py** => utility functions
- **explore.py** => explore data and find problems
- **audit_street_names.py** => find bad street names
- **check_correct.py** => functions used to correct tags
- **cleaning.py** => main script for cleaning and saving csv files

Furthermore, the 'schema.py' can be used to validate the formatting of the data 
before saving it as CSV.

### Data analysis and cleaning

To explore the data and find possible issues, I created a 'explore.py' script. 
It allows me to have a look into the ways, nodes and tags and select individual elements for further analysis.

The script takes two arguments: the name of the OSM file and the type of tags 
that shall be analysed ('way' or 'tag'). After reading the data, it lists the 
most common tag types. This is helpful as an overview for further exploring.

Also, there is an overview of the top 10 tag types and their most common values.

After this general information, there is a prompt that asks for a tag type. This
allows to list all values of a tag type, ordered by number of occurrences.

The script can be used to find problems in the data. For example if we enter 'addr:city',
we can finde some wrong values - e.g. 'MÜ', 'Müchen', 'Muchen', etc. While these 
kind of problems can not be spotted programatically, we create a text file with all 
the misspelled Names of Munich ('munich-names.txt'). We later use this file to recognize bad values and substitute it by the correct one.

Looking at the city names ('addr:city') we see that there are different spellings 
for the same cities. We correct this by creating a mapping file called 'city-names.txt'. 
This includes the duplicate/wrong value and maps it to the correct value.

A last mapping file is created for the street names ('addr:street'). First we find 
typos programatically and then map these wrong values to the right ones. We save the 
mapping as 'stree-names.txt'.

More details about the encountered problems and their handling can be found in the next section.

The functions for spotting problematic data and correcting it, is included in the 
'check_and_correct.py' script. This is then used by the major 'cleaning.py' script 
that walks through the OSM data, corrects it if necessary and exports everything 
to csv files.

Finally, the csv files are imported into an sqlite database called ‘munich.db’.

## Problems 
### Problems in Node Tags

**addr:country**

Includes Austria

Strangely, there is one node that states 'Austria' instead of 'Germany' as county. If we look at the other details, we clearly see that it is a hotel in the city center ('Hotel Motel One Sendlinger Tor'). We will correct this in our cleaning process and replace the country with 'Germany' (or with its code 'DE' to be precise).

**addr:city**

Wrong values:
```
- MÜ
- Müchen
- Muchen
- münchen
```

Looking at the city names, we can easily see a lot of different spellings of 'München'. This will be corrected during the cleaning process.

### Problems in Way Tags

**addr:city**

Wrong or duplicate values:
```
- Pullach, Pullach i./im Isartal
- Aschheim, aschheim
- Munich, Münschen, Müchen
- Kartlsfeld
- Grünwald, Grünwald bei München
- Garchin, Garching bei München
- Ingolstadt
```

As in the Node tags, the city names include quite a few spelling errors. We will fix this in the cleaning process.

### Street Name Audit
A special script is used to audit the street names ('audit_street_names.py'). It loops through the tags of type 'addr:street' and applies a regular expression to check, if the street name is well formed.

The result of the programatic audit was saved as text file ('audited-street-names.txt') and  evaluated manually, to build a list of street names that are actually wrong.

Surprisingly, this revealed only a hand full of obviously misspelled values. These were:
```
1. Breslauer Straße 
2. Planegger Str.
3. münchnerstr
4. Gutenbergstraßw
5. Münchener Str.
```

There is one clear typo (1.), three unexpected abbreviations (2., 3., 5.) and a trailing space in the first one. 

A file was created to map the wrong values to the correct ones (colon separated).
```
Breslauer Straße :Breslauer Straße
Planegger Str.:Planegger Straße
münchnerstr:Münchner Straße
Gutenbergstraßw:Gutenbergstraße
Münchener Str.:Münchner Straße
```

One funny value occurred in the data named 'Lueg ins Land' which translates to 'Lie into the country'. Though, being a Munich citizen, I was not aware of such a street and it sounded like a joke. However, a quick research revealed that there is actually a tower and a street in front of it named so.

### Numeric Values Audit

Numeric values like postal codes or phone numbers are expected to be in a well defined form.

By using our 'explore.py' script we can quickly extract the postcodes. There are 98 unique codes in the Munich data set. All are matching the expected form of five digits.

Lets continue with phone numbers.

Looking at the values of the 'phone' tags, we can clearly see a lot of differences in the formatting. Here is an excerpt:

```
089618989
+49 89 21268470
+49 89 988100
+49 89 202044000
+49 (0) 157 / 92 333 115
089 (0)172 850 98 00
+49 89 58929632
+49 (0)8142 4104076
+49 89 45216652
+49 89 1504035
...
```

There are different forms for the country code ('+49'), for the city code ('89') and the number in general. Besides landline numbers we can also find mobile phone numbers and numbers from different cities (or even other countries).

For our further investigation of the data, we only want to include landline numbers from Munich and mobile phone numbers. 
Furthermore, we want to make sure that the numbers are having the same format. 
All numbers should have the form '+49 89 *landline number*' or '+49 *mobile pre number (space) mobile number*'. 

This is achieved with a regular expression that matches the valid parts. 
The last group of the regex is the main number. We remove any special characters or whitspaces from it and append it to the standard prefix. For landline the prefix is always '+49 89 ' and for mobile it is '+49 ' plus the mobile pre-number that we get from the second last regex group.

During the cleaning process we substitute valid numbers with the harmonized ones. If the number is not valid (no regex match), we re-name the tag key to 'phone_bad'. This way all phone numbers in the phone tag are well-formed, but also keep the bad formed for reference.

## General statistics

### File sizes
```
munich_germany.osm      486 MB
munich.db               274 MB
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
Let's first have a look how many users there are in each of the 'nodes' and 'ways:

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

Now we want to combine the two user columns from each table and count the total number of unique users:

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
 LIMIT 10                                                          
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
```


## Tags

### Top tag types
To further analyse the nodes and tags, we want to know which types of tags are available:

```sql
sqlite> SELECT key, COUNT() AS num
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
... 
```
*(resulting table shortened for presentation purposes)*

### Number of amenities

```sql
sqlite>SELECT value, count() 
FROM nodes_tags 
WHERE key="amenity" 
GROUP BY value 
ORDER BY COUNT() DESC 
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
Let's create a more informative query. We want to get all cafes with their name and latitude/longitude:

```sql
SELECT nodes.id,lat,lon,names.value 
FROM 
    (SELECT * FROM nodes_tags 
    WHERE key="amenity" and value="cafe") AS cafes, 
    (SELECT * FROM nodes_tags WHERE key="name") AS names, 
    nodes 
WHERE 
    cafes.id=nodes.id 
    AND names.id=cafes.id;

```

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
*(resulting table shortened for presentation purposes)*

### Most popular cuisines
Having a look at the 'keys' in 'nodes_tags', we can spot 'cuisine'. With this we can find out the most popular cuisines in the city:

```sql
sqlite>SELECT value, count() AS num
FROM nodes_tags
WHERE key="cuisine"
GROUP BY value
ORDER BY num DESC
LIMIT 10;
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
```

### Leisure nodes
Another interesting tag is 'leisure'. Here is an overview of the top 20 values of that key:

```sql
sqlite>SELECT value, count() AS num 
FROM nodes_tags 
WHERE key="leisure" 
GROUP BY value 
ORDER BY num DESC 
LIMIT 10;
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
```

## Ways

### Top tag types - ways

```sql
sqlite> SELECT key, COUNT() AS num
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
...
```
(resulting table shortened for presentation purposes)

### Speed limits

```sql
sqlite> SELECT value, COUNT() AS num
FROM ways_tags
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

While there are some strange values, we can clearly see that the most common speed limit is 30 km/h followed by 50 km/h.


### Natural ways

```sql
sqlite> SELECT value, COUNT() AS num
FROM ways_tags
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
We could combine the position of cafes with position of trees (node type 'natural'). This way we could find out which cafes are embedded in the greenest area. An idea would be to plot the cafe positions on a map and use the number of trees in a defined radius as a circle size. The cafes with the most trees around them, would have big green circles.

### Possible problems
Probably not every tree is marked with a node. It is likely that clusters of trees are marked by only one node. This could distort the outcome.

Also, what if there are areas, where more trees are marked than in others?
