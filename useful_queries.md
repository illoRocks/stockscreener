# Useful Queries

Only show the latest values.

```js
ciks = ["796343"]
labels = ["Revenues"]
db.financialPositions.aggregate([
    // {"$match": {"cik": {"$in": ciks }}},
    // {"$match": {"label": {"$in": labels }}},
    {"$group": {
        "_id": {
            "startDate": "$startDate",
            "endDate": "$endDate",
            "instant": "$instant",
            "duration": "$duration",
            "segment": "$segment",
            "label": "$label",
            "cik": "$cik"
        },
        "latest": {"$max": "$updated"},
        "doc": {"$push": "$$ROOT"}
    }},
    {"$unwind": "$doc"},
    {"$redact": {"$cond": [
            {"$eq": ["$doc.updated", "$latest"]},
            "$$KEEP",
            "$$PRUNE"
        ]
    }},
    {"$project": {
        "_id": "$doc._id",
        "startDate" : "$_id.startDate",
        "endDate" : "$_id.endDate",
        "instant" : "$_id.instant",
        "duration" : "$_id.duration",
        "label" : "$_id.label",
        "cik": "$_id.cik",
        "segment": "$_id.segment",
        "value": "$doc.value"
    }},
])
```

Only show yearly reports.

(coming soon)

Only show consolidated values.

(comming soon)

Clear database

```js
db.reports.drop()
db.companies.drop()
db.segments.drop()
db.paths.update({}, {'$set': {'log': null}})
```