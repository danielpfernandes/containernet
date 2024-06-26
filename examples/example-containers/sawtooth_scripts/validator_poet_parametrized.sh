#!/bin/bash

if [ -z "$1" ]; then
    echo "Invalid command, pass one of the following arguments:"
    echo "validator_parametrized.sh <argument>"
    echo "  Valid arguments: base1, drone"
    exit 1
fi

rm -rf /var/lib/sawtooth/*
rm -rf /var/log/sawtooth/*

IP=$(hostname -I | awk '{print $2}')
VALIDATOR=""
PEERS=""
BASE1_IP='10.0.0.1'
VALIDATOR_PRIV="/etc/sawtooth/keys/validator.priv"

#while IFS="" read -r p || [ -n "$p" ]; do
#    if [ "$p" != "$IP" ]; then
#        if [ -z "$PEERS" ]; then
#            PEERS="tcp://$p:8800"
#        else
#            PEERS="$PEERS,tcp://$p:8800"
#        fi
#    fi
#done < /data/drones.txt
if [ "$IP" != "$BASE1_IP" ]; then
  while IFS="" read -r p || [ -n "$p" ]; do
      if [ "$p" == "$IP" ]; then
        COUNTER=0
        while IFS="" read -r q || [ -n "$q" ] ; do
          ((COUNTER++))
          if [ "$COUNTER" -lt 4 ]; then
            if [ -z "$PEERS" ]; then
                PEERS="tcp://$q:8800"
            else
                PEERS="$PEERS,tcp://$q:8800"
            fi
          fi
        done
      fi
  done < /data/drones.txt
else
  COUNTER=0
  while IFS="" read -r p || [ -n "$p" ]; do
    ((COUNTER++))
      if [ "$p" != "$IP" ]; then
        if [ "$COUNTER" -lt 4 ]; then
          if [ -z "$PEERS" ]; then
              PEERS="tcp://$p:8800"
          else
              PEERS="$PEERS,tcp://$p:8800"
          fi
        fi
      fi
  done < /data/drones.txt
fi
case $1 in
base1)  VALIDATOR='0'
  echo "Base $VALIDATOR with peers $PEERS";;
drone) VALIDATOR='1'
  if [ -z "$PEERS" ]; then
    PEERS="tcp://$BASE1_IP:8800"
  else
    PEERS="tcp://$BASE1_IP:8800,$PEERS"
  fi
    echo "Drone $IP with peers $PEERS"
    sleep 5;;
*) echo "Invalid option";;
esac 

    sawadm keygen --force &&

if [ $VALIDATOR == '0' ];
    then
    poet enclave measurement > poet-enclave-measurement &&
    poet enclave basename > poet-enclave-basename &&
    cp /etc/sawtooth/simulator_rk_pub.pem / &&
    poet registration create -k $VALIDATOR_PRIV -o poet.batch &&

    sawset genesis -k $VALIDATOR_PRIV -o config-genesis.batch &&
    
    sawset proposal create --key $VALIDATOR_PRIV \
        -o config-consensus.batch \
        sawtooth.consensus.algorithm.name=PoET \
        sawtooth.consensus.algorithm.version=0.1 \
        sawtooth.poet.report_public_key_pem="$(cat simulator_rk_pub.pem)" \
        sawtooth.poet.valid_enclave_measurements="$(cat poet-enclave-measurement)" \
        sawtooth.poet.valid_enclave_basenames="$(cat poet-enclave-basename)" &&
    
    sawset proposal create --key $VALIDATOR_PRIV \
        -o poet-settings.batch \
        sawtooth.poet.target_wait_time=5 \
        sawtooth.poet.initial_wait_time=60 \
        sawtooth.poet.ztest_minimum_win_count=999999999 \
        sawtooth.publisher.max_batches_per_block=100 &&

    sawadm genesis config-genesis.batch config-consensus.batch poet.batch poet-settings.batch

    sawtooth keygen root --force &&
    sawtooth-validator -vv \
    --endpoint tcp://"${IP}":8800 \
    --bind network:tcp://"${IP}":8800 \
    --bind component:tcp://"${IP}":4004 \
    --peering dynamic \
    --peers "$PEERS" \
    --seeds "$PEERS" \
    --scheduler parallel \
    --network-auth trust

else

    sawtooth keygen root --force &&
    sawtooth-validator -vv \
    --endpoint tcp://"${IP}":8800 \
    --bind network:tcp://"${IP}":8800 \
    --bind component:tcp://"${IP}":4004 \
    --peering dynamic \
    --peers "$PEERS" \
    --seeds "$PEERS" \
    --scheduler parallel \
    --network-auth trust

# ##### Other options
# #    --bind component:tcp://127.0.0.1:4004 \
# #    --bind consensus:tcp://127.0.0.1:5050 \
# #    --bind network:tcp://127.0.0.1:8800 \
# #    --scheduler parallel \
# #    --peering static \
# #    --maximum-peer-connectivity 10000 \

fi
