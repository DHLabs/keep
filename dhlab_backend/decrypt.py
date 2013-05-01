from backend.db import db, decrypt_survey


def main():
    surveys = db.survey.find()

    for survey in surveys:
        print 'Decrypting data for %s' % ( survey[ '_id' ] )

        data = db.survey_data.find( { 'survey': survey[ '_id' ] } )

        for datum in data:
            datum[ 'data' ] = decrypt_survey( datum[ 'data' ] )
            datum[ 'repo' ] = datum[ 'survey' ]
            del datum[ 'survey' ]

            db.data.insert( datum )


if __name__ == '__main__':
    main()
