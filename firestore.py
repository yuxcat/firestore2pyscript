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

log_ref = db.collection('logs').document('123').set({ 'time' : 12, 'plate': 1234})
print(log_ref)
