import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account to create a private key, then output it as json
cred = credentials.Certificate('./avmsystem-9811f-firebase-adminsdk-xxxx-xxxxx.json')
firebase_admin.initialize_app(cred)

db = firestore.client()


# Then query for documents 
# I'm retreiving license info from "plates" Doc collection

plates_ref = db.collection(u'plates')

for doc in plates_ref.stream():
    print(u'{} => {}'.format(doc.id, doc.to_dict()))
    
    #printing specific field on collection
    print(u'{},{}'.format(doc.id, doc.to_dict().get('your_field_name')))

    
#inserting data to firestore using python 2.7
#getting current time
now = firestore.SERVER_TIMESTAMP

log_ref = db.collection('logs').document('123').set({ 'time' : (now), 'plate': 1234})
print(log_ref)

#querying firebase for doc.id / collection

plate_owner = plates_ref.where(u'plate', u'==', u'KL6036').stream()

for doc in plate_owner:
    print(u'{} => {}'.format(doc.id, doc.to_dict()))
