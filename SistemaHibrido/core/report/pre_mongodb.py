def pre_processamento(banco):
    banco.intermediaria_processado.aggregate([
        { "$match": { "action": "viewed" } },       
        { "$group": { "_id": "$userid", "Total_Viewed": { "$sum": 1 } } },
        { "$out": "Total_Viewed"}
    ])

    banco.intermediaria_processado.aggregate([
        { "$match": { "action": "viewed" , "target": "attempt"} },       
        { "$group": { "_id": "$userid", "Created_Submission": { "$sum": 1 } } },
        { "$out": "Created_Submission"}
    ])

    banco.intermediaria_processado.aggregate([        
        { "$match": { "action": "viewed" , "target": "submission_form"} },       
        { "$group": { "_id": "$userid", "Viewed_Submission_Form": { "$sum": 1 } } },
        { "$out": "Viewed_Submission_Form"}
    ])

    banco.intermediaria_processado.aggregate([        
        { "$match": { "action": "created" , "target": "post"} },       
        { "$group": { "_id": "$userid", "Created_Post": { "$sum": 1 } } },
        { "$out": "Created_Post"}
    ])

    banco.intermediaria_processado.aggregate([        
        { "$match": { "action": "viewed" , "target": "discussion"} },       
        { "$group": { "_id": "$userid", "Viewed_Discussion": { "$sum": 1 } } },
        { "$out": "Viewed_Discussion"}
    ])

    banco.intermediaria_processado.aggregate([       
        { "$match": { "action": "created" , "target": "discussion_subscription"} },       
        { "$group": { "_id": "$userid", "Created_Discussion_Subscription": { "$sum": 1 } } },
        { "$out": "Created_Discussion_Subscription"}
    ])

    banco.intermediaria_processado.aggregate([       
        { "$match": { "action": "viewed" , "target": "grade_report"} },       
        { "$group": { "_id": "$userid", "Viewed_Grade_Report": { "$sum": 1 } } },
        { "$out": "Viewed_Grade_Report"}
    ])

    banco.intermediaria_processado.aggregate([       
        { "$match": { "action": "viewed" , "target": "course"} },       
        { "$group": { "_id": "$userid", "Viewed_Course": { "$sum": 1 } } },
        { "$out": "Viewed_Course"}
    ])

    banco.intermediaria_processado.aggregate([     
        { "$match": { "action": "viewed" , "target": "message"} },       
        { "$group": { "_id": "$userid", "Viewed_Message": { "$sum": 1 } } },
        { "$out": "Viewed_Message"}
    ])

    banco.intermediaria_processado.aggregate([        
        { "$group": { "_id": "$userid", "Total_Action": { "$sum": 1 } } },
        { "$out": "Total_Action"}
    ])

    banco.intermediaria_processado.aggregate([ 
        { "$match": { "action": "created" } },
        { "$group": { "_id": "$userid", "Total_Created": { "$sum": 1 } } },
        { "$out": "Total_Created"}
    ])

    banco.intermediaria_processado.aggregate([        
        { "$match": { "action": "viewed" , "target": "course_module"} },       
        { "$group": { "_id": "$userid", "Viewed_Course_Module": { "$sum": 1 } } },
        { "$out": "Viewed_Course_Module"}
    ])

    banco.intermediaria_processado.aggregate([       
        { "$match": { "action": "viewed" , "target": "submission_status"} },       
        { "$group": { "_id": "$userid", "Viewed_Submission_Status": { "$sum": 1 } } },
        { "$out": "Viewed_Submission_Status"}
    ])

    banco.Total_Action.aggregate([

    {
        "$lookup":{
            "from": "Created_Post",       
            "localField": "_id",   
            "foreignField": "_id", 
            "as": "total"         
        }
    },

    {
        "$lookup":{
            "from": "Created_Submission",       
            "localField": "_id",   
            "foreignField": "_id", 
            "as": "total2"         
        }
    },

    {
        "$lookup":{
            "from": "Created_Discussion_Subscription",       
            "localField": "_id",   
            "foreignField": "_id", 
            "as": "total3"         
        }
    },

    {
        "$lookup":{
            "from": "Total_Created",       
            "localField": "_id",   
            "foreignField": "_id", 
            "as": "total4"         
        }
    },

    {
        "$lookup":{
            "from": "Total_Viewed",       
            "localField": "_id",   
            "foreignField": "_id", 
            "as": "total5"         
        }
    },

    {
        "$lookup":{
            "from": "Viewed_Course",       
            "localField": "_id",   
            "foreignField": "_id", 
            "as": "total6"         
        }
    },

    {
        "$lookup":{
            "from": "Viewed_Course_Module",       
            "localField": "_id",   
            "foreignField": "_id", 
            "as": "total7"         
        }
    },

    {
        "$lookup":{
            "from": "Viewed_Discussion",       
            "localField": "_id",   
            "foreignField": "_id", 
            "as": "total8"         
        }
    },

    {
        "$lookup":{
            "from": "Viewed_Grade_Report",       
            "localField": "_id",   
            "foreignField": "_id", 
            "as": "total9"         
        }
    },

    {
        "$lookup":{
            "from": "Viewed_Message",       
            "localField": "_id",   
            "foreignField": "_id", 
            "as": "total10"         
        }
    },

    {
        "$lookup":{
            "from": "Viewed_Submission_Form",       
            "localField": "_id",   
            "foreignField": "_id", 
            "as": "total11"         
        }
    },

    {
        "$lookup":{
            "from": "Viewed_Submission_Status",       
            "localField": "_id",   
            "foreignField": "_id", 
            "as": "total12"         
        }
    },

    {
        "$lookup":{
            "from": "Viewed_Attempt",       
            "localField": "_id",   
            "foreignField": "_id", 
            "as": "total13"         
        }
    },

    {
        "$replaceRoot": { "newRoot": { "$mergeObjects": [ { "$arrayElemAt": [ "$total", 0 ] },
    { "$arrayElemAt": [ "$total2", 0 ] },
    { "$arrayElemAt": [ "$total3", 0 ] },
    { "$arrayElemAt": [ "$total4", 0 ] },
    { "$arrayElemAt": [ "$total5", 0 ] },
    { "$arrayElemAt": [ "$total6", 0 ] },
    { "$arrayElemAt": [ "$total7", 0 ] },
    { "$arrayElemAt": [ "$total8", 0 ] },
    { "$arrayElemAt": [ "$total9", 0 ] },
    { "$arrayElemAt": [ "$total10", 0 ] },
    { "$arrayElemAt": [ "$total11", 0 ] },
    { "$arrayElemAt": [ "$total12", 0 ] },
    { "$arrayElemAt": [ "$total13", 0 ] }, "$$ROOT" ] } }},

    { "$project": {"total": 0,
    "total2": 0,
    "total3": 0,
    "total4": 0,
    "total5": 0,
    "total6": 0,
    "total7": 0,
    "total8": 0,
    "total9": 0,
    "total10": 0,
    "total11": 0,
    "total12": 0,
    "total13": 0 }},
        {"$out":"processado"}
    ])

    banco.Total_Viewed.drop()
    banco.intermediaria_processado.drop()
    banco.Total_Action.drop()
    banco.Total_Created.drop()
    banco.Created_Discussion_Subscription.drop()
    banco.Created_Post.drop()
    banco.Created_Submission.drop()
    banco.Viewed_Attempt.drop()
    banco.Viewed_Course.drop()
    banco.Viewed_Course_Module.drop()
    banco.Viewed_Discussion.drop()
    banco.Viewed_Grade_Report.drop()
    banco.Viewed_Message.drop()
    banco.Viewed_Submission_Form.drop()
    banco.Viewed_Submission_Status.drop()  