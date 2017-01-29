# Problems in Munich OSM Data
This document lists the proplems found in the Munich OSM data during data wrangling and how these problems are addressed. The issues are separated by 'ways' and 'nodes' tags, as well as by the tag key.

## Nodes Tags

### name
-> all kind of different data, e.g.:
- Numbers (5,224,4)
- Street names (Wilhelm-Kuhnert-Straße)
- Shops (dm, Penny Markt, Netto)
- City areas (München-Pasing)

This tag alone will not be suitable for automatic processing such as clustering. We will keep this in mind for our analysis later.

### entrance
Inludes both 'yes' and specific titles:

15786   yes
2943    main
34      service
23      emergency
21      exit
10      back
5       staircase
5       es
3       delivery
3       gate
1       barrier
1       secondary_entrance

Most of the entrances are just marked as 'yes' or 'main'. More specific labels, such as 'service' or 'emergency', are very rare. Therefore, this tags are not a good source for categorizing.

### addr:country
Includes Austria - 

Strangely, there is one node that states 'Austria' instead of 'Germany' as county. If we look at the other details, we clearly see that it is a hotel in the city center ('Hotel Motel One Sendlinger Tor'). We will correct this in our cleaning process and replace the country with 'Germany' (or with its code 'DE' to be precise).

### addr:city
Wrong values:
- MÜ
- Müchen, Muchen, münchen, München???

Looking at the city names, we can easily see a lot of different spellings of 'München'. This will be corrected during the cleaning.

### natural
Includes some strange values like 'mushroom':
19635   tree
24      peak
13      mushroom
12      spring
4       tree_group
3       stone
2       scrub
1       wood
1       cave_entrance

This is an other example where almost all tags have one value - 'tree' - but some have special ones. Looking at the numbers, one could argue to replace all non-tree tags with 'other'. However, it seems logical that 'peak' only appears very rarely compared to 'tree'. We will leave this for now as it is.


## Ways Tags

### addr:city
Wrong or dublicate values:
- Pullach, Pullach i./im Isartal
- Aschheim, aschheim
- Munich, Münschen, Müchen
- Kartlsfeld
- Grünwald, Grünwald bei München
- Garchin, Garching bei München
- Ingolstadt

As in the Node tags, the city names inlude quite a few spelling errors. We will fix this in the cleaning process.

### source
Similar or dublicate values:
- Bing, bing, bing_imagery
- Yahoo, yahoo, ...

This tag inludes different spellings for - what seems to be - the same source. Though, it is sometimes hard to say, if it is just a different spelling or actually a different source.

We will leave it as it is, because we will not analyse the source.

### building
A lot of strange or wrong values, for example:
y, ^yes, 5, #CCCCCC, no

The values of this include some strang or obviously wrong values. It seems not feasible to automaticaly clean this. We will leave it as it is and keep it in mind for the analysing part.

### addr:housenumber
Very different formating, most entities occur only once:
- extra characters ('a','b','c',...), attached differentely
- extra description ('Rgb.')
- ranges (comma seperated, '-', ';')

The values in this tag are unfortunately formated very differently. Sometimes there are extra characters or descriptions attached and there are cases describing ranges in different manners (different characters). Once again, we will not change this, because it seems impossible to do this programatically.
    

## Street Name Audit
A special script is used to audit the street names ('audit_street_names.py'). It loops through the tags of type 'addr:street' and applies a regular expression to check, if the street name is well formed.

The result of the programatic audit was saved as text file ('audited-stree-names.txt') and  evaluted manually, to build a list of street names that are actually wrong.

Surprisingly, this revealed only a hand full of obviously misspelled values. These were:

1. Breslauer Straße 
2. Planegger Str.
3. münchnerstr
4. Gutenbergstraßw
5. Münchener Str.

There is one clear typo (1.), three unexpected abrevations (2., 3., 5.) and an extra space in the first one. 

A file was created to map the wrong values to the correct ones during the data import.

- Breslauer Straße :Breslauer Straße
- Planegger Str.:Planegger Straße
- münchnerstr:Münchner Straße
- Gutenbergstraßw:Gutenbergstraße
- Münchener Str.:Münchner Straße

One funny value occured in the data named 'Lueg ins Land' which translates to 'Lie into the country'. Though, being a Munich citizen, I was not aware of such a street and it sounded like some joke. However, a quick research revealed that there is actually a tower named and a street in front of it named so.
