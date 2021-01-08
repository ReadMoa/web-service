echo ----------------------------------------------
echo START deploy process
echo ----------------------------------------------

cd webapp
npm run-script build
cd ..
gcloud app deploy app.standard.prod.yaml

echo ----------------------------------------------
echo COMPLETED deploy process
echo ----------------------------------------------