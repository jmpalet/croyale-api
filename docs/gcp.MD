###Steps to create a GKE Application with static inbound and outbound IPs:

1. Create cluster:
```
gcloud container clusters create $CLUSTER_NAME -gi-num-nodes=$CLUSTER_NUM_NODES
```

2. Create static IPs (inbound and outbound):
```
gcloud compute addresses create $OUTBOUND_IP_NAME --region $OUTBOUND_IP_REGION
gcloud compute addresses create $INBOUND_IP_NAME --region $INBOUND_IP_REGION
```

3. List the created IP addresses and save `$OUTBOUND_IP_ADDRESS`:
```
gcloud compute addresses list
```

4. Get instance ids:
```
gcloud compute instances list
```

5. For each instance id `$VM_INSTANCE_ID` and $VM_INSTANCE_ZONE set outbound ip with `$OUTBOUND_IP_ADDRESS`:
```
gcloud compute instances delete-access-config $VM_INSTANCE_ID --access-config-name external-nat --zone=$VM_INSTANCE_ZONE
gcloud compute instances add-access-config $VM_INSTANCE_ID --access-config-name external-nat --address $OUTBOUND_IP_ADDRESS --zone=$VM_INSTANCE_ZONE
```

6. Deploy Kubernetes
```
kubectl apply -f *.yaml
```