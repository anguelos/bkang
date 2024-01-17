#!/bin/bash

DRY_RUN=0 # 0 for real run, 1 for dry run

# Config variables start here
EXCLUDE=" --exclude environments --exclude .cache --exclude tmp --exclude .local --exclude anaconda3 --exclude .conda --exclude .config --exclude .mozilla --exclude .thunderbird  --filter='- .ssh/id_*' "
EXCLUDE=" --exclude=.cache --exclude=tmp --exclude=.local --exclude=anaconda3 --exclude=.conda --exclude=.config --exclude=.mozilla --exclude=.thunderbird  --filter='- .ssh/id_*' "
SRV=127.0.0.1

SRCDIR=/home  # The absolute path to the directory to back-up
#SRCDIR=/home/anguelos/work/src/ptlbp/

SRVDIR=/mnt/backup # The directory on the server to store the back-ups
#SRVDIR=/tmp/bkup

CURRENTDIR="${SRVDIR}/current/${SRCDIR}"
ARCHIVEDIR="${SRVDIR}/archive"
DATEDIRCMD="${ARCHIVEDIR}/$(date -I)"
# Config variables end here


MODE="BACKUP"


case $MODE in 
    "BACKUP")
        STARTDATE=$(date)

        echo "Starting back-up at ${STARTDATE}"
        echo "Dry run: ${DRY_RUN}"
        echo "Source directory: ${SRCDIR}"
        CMD="ssh ${SRV} mkdir -p ${CURRENTDIR} && echo 'created current dir' || echo 'could not create current dir' || exit"
        echo $CMD
        eval $CMD  # Even in dryrun we create the current dir


        # Check if archive exists (or is beeing currently written) and abort if so
        CMD="ssh ${SRV} ls ${DATEDIRCMD} &&  echo 'bkup already there aborting' && ssh ${SRV} 'echo ${STARTDATE} ARCHIVE FOUND, Aborting >>${SRVDIR}/log' && exit"
        echo $CMD
        eval $CMD  # Even in dryrun should be exiting here

        echo "Archive not found, continuing with back-up"

        # Rsync to server
        CMD="rsync -avh ${EXCLUDE} --progress --delete ${SRCDIR}/ ${SRV}:${CURRENTDIR}/ && echo 'rsync done' || echo 'rsync failed'"
        echo $CMD
        if [ $DRY_RUN -eq 0 ]; then
            eval $CMD
        fi

        # Create archive and copy to server with hard links
        CMD="ssh ${SRV} \"mkdir -p ${SRVDIR}/archive\" || echo 'could not create archive' exit"
        echo $CMD
        if [ $DRY_RUN -eq 0 ]; then
            eval $CMD
        fi


        CMD="ssh ${SRV} \"mkdir -p ${DATEDIRCMD} && cd ${SRVDIR} && cp -al ${CURRENTDIR} ${DATEDIRCMD} && echo 'STARTED ${STARTDATE}   FINISHED   $(date)' OK >>${SRVDIR}/log\" "
        echo $CMD
        if [ $DRY_RUN -eq 0 ]; then
            eval $CMD
        fi
        ;;
    
    "INSTALL")
        echo "Not implemented yet!"
        ;;
esac