# Useful Queries

## Only show the latest values

```javascript
db.reports.aggregate(
    [
        { $group:
                { _id: {
                        company: "$company",
                        label: "$label",
                        segment: "$segment",
                        instant: "$instant",
                        startDate: "$startDate",
                        endDate: "$endDate" },
                    lastSalesDate: { $last: "$updated" },
                    entries: { $push: "$$ROOT" } }
        },
        { $replaceRoot: { newRoot: { $arrayElemAt: ["$entries", 0] }}}
    ])
```

## Only show consolidated values

```javascript
db.reports.aggregate(
    [
        { $match: { segment: { "$exists": false }}}
    ])
```

## Only show yearly reports

```javascript
var labels = ["Revenues"]
var ciks = ["796343"]
var quarter = {
    q4: [350, 370],
    q3: [260, 280],
    q2: [170, 190],
    q1: [70, 100]
}

db.reports.aggregate(
    [
        { $group:
                { _id: {
                        company: "$company",
                        label: "$label",
                        segment: "$segment",
                        instant: "$instant",
                        startDate: "$startDate",
                        endDate: "$endDate" },
                    lastSalesDate: { $last: "$updated" },
                    entries: { $push: "$$ROOT" } }},
        { $replaceRoot: { newRoot: { $arrayElemAt: ["$entries", 0] }}},
        { $match: { company: {"$in": ciks }}},
        { $match: { label: {"$in": labels }}},
        { $match: { segment: { "$exists": false }}},
        { $match: { duration: {
            "$gte": quarter.q4[0],
            "$lte": quarter.q4[1]
        }}},
        { $sort: { endDate: 1 }}
    ])
```

## Show company with filtered financial positions

```javascript
var labels = ["Revenues"]

var pipeline = [
    // # filter latest
    {'$group':
        {'_id': {
                'company': "$company",
                'label': "$label",
                'segment': "$segment",
                'instant': "$instant",
                'startDate': "$startDate",
                'endDate': "$endDate"
            },
            'lastSalesDate': { "$last": "$updated" },
            'entries': { '$push': "$$ROOT" }
        }
    },
    { '$replaceRoot': { 'newRoot': { '$arrayElemAt': ["$entries", 0] } } },

    // # filter labels
    { '$match': { 'label': { "$in": labels } } },

    // # not use segment values
    { '$match': { 'segment': { "$exists": false } } },

    // # sort by date
    { '$sort': { 'endDate': 1 } },

    // # reports as array property
    {
        '$group':
            {
                '_id': "$company",
                'reports': {
                    '$push': {
                        _id: "$$ROOT._id",
                        endDate: "$$ROOT.endDate",
                        value: "$$ROOT.value",
                        label: "$$ROOT.label",
                        updated: "$$ROOT.updated",
                        duration: "$$ROOT.duration",
                        startDate: "$$ROOT.startDate"
                    }
                }
            }},

    // // # join with compny collection
    {'$lookup': {
        'from': "companies",
        'localField': "_id",
        'foreignField': "_id",
        'as': "company"}},
    { '$unwind': "$company" },

    {'$project': {
        'reports': 1,
        'lastUpdate': "$company.lastUpdate",
        'NumberOfDocuments': "$company.NumberOfDocuments",
        'EntityRegistrantName': "$company.EntityRegistrantName",
        'CurrentFiscalYearEndDate': "$company.CurrentFiscalYearEndDate"}},

    // // # write to new collection
    {'$out': 'transformed'}
]

db.reports.aggregate(pipeline)
```

Result:

```json
{
  "_id" : "796343",
  "reports" : [
    {
      "_id" : ObjectId("5aab0b23061b2912fe6a3534"),
      "endDate" : ISODate("2007-11-30T01:00:00.000+01:00"),
      "duration" : NumberInt("363"),
      "label" : "Revenues",
      "updated" : ISODate("2010-01-22T01:00:00.000+01:00"),
      "startDate" : ISODate("2006-12-02T01:00:00.000+01:00"),
      "company" : "796343",
      "value" : NumberLong("3157881000")
    },
    {
      "_id" : ObjectId("5aab0b18061b2913006a36da"),
      "endDate" : ISODate("2008-11-28T01:00:00.000+01:00"),
      "duration" : NumberInt("363"),
      "label" : "Revenues",
      "updated" : ISODate("2011-01-27T01:00:00.000+01:00"),
      "startDate" : ISODate("2007-12-01T01:00:00.000+01:00"),
      "company" : "796343",
      "value" : NumberLong("3579889000")
    },
    // ...
  ],
  "lastUpdate" : ISODate("2018-03-16T02:10:14.760+01:00"),
  "NumberOfDocuments" : NumberInt("49"),
  "EntityRegistrantName" : "ADOBE SYSTEMS INC",
  "CurrentFiscalYearEndDate" : "--11-27"
}
```

## Clear database

```js
db.reports.drop()
db.companies.drop()
db.segments.drop()
db.paths.update({}, {'$set': {'log': null}})
```
