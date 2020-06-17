# Cuckoopy
A cuckoo filter implementation based on the [Cuckoopy library](https://github.com/rajathagasthya/cuckoopy).
Cuckoo filters hash input elements when inserting a new element. However, datashare is using the filter
for hashed tags which makes the initial hash redundant. Therefore, we removed the initial hash.


