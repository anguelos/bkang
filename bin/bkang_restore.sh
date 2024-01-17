#!/bin/bash

DRY=1

users=("anguelos" "atzenhofer" "bkang"  "nicolas"  "nprenet" "sandyaoun" "tamas" "tosques" "tschernn" "vogeler" "winslows")

users=$(ls /mnt/backup/current/home)

echo "Restoring DRY=${DRY} users=${users}"

for username in ${users[@]}; 
do
  echo "looking for '${username}'"
  useradd -m ${username} -s /bin/bash || continue
  echo "${username} not found. Restoring from backup"

  CMD="cp -Rp /mnt/bkup/current/home/${username} /home/ "
  if [[ $DRY -eq 1 ]]; then
    echo $CMD
  else 
    echo $CMD
    eval $CMD
  fi

  CMD="chown -R  ${username}.${username} /home/${username} "
  if [[ $DRY -eq 1 ]]; then
    echo $CMD
  else 
    echo $CMD
    eval $CMD
  fi  
    
  CMD="sudo -u ${username} ssh-keygen  -t rsa -N '' -f /home/${username}/.ssh/id_rsa"
  if [[ $DRY -eq 1 ]]; then
    echo $CMD
  else 
    echo $CMD
    eval $CMD
  fi
  
  # adding self to authorized keys
  CMD="cat /home/${username}/.ssh/id_rsa.pub >> /home/${username}/.ssh/authorized_keys"
  if [[ $DRY -eq 1 ]]; then
    echo $CMD
  else 
    echo $CMD
    eval $CMD
  fi
  
  # Removing duplicates in authorized keys
  CMD="cp /home/${username}/.ssh/authorized_keys /home/${username}/.ssh/authorized_keys.bkup; cat  /home/${username}/.ssh/authorized_keys.bkup | sort|uniq > /home/${username}/.ssh/authorized_keys"
  if [[ $DRY -eq 1 ]]; then
    echo $CMD
  else 
    echo $CMD
    eval $CMD
  fi
  
  # Forcing .ssh/authorized_keys permissions to 600
  CMD="chmod 600 /home/${username}/.ssh/authorized_keys; chown ${username}.${username} /home/${username}/.ssh/authorized_keys"
  if [[ $DRY -eq 1 ]]; then
    echo $CMD
  else 
    echo $CMD
    eval $CMD
  fi
    
  echo ""
done
