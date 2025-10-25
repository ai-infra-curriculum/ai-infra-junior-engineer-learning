# Module 006: Kubernetes Introduction - Assessment Quiz

## Instructions

This quiz contains 25 questions covering all aspects of Module 006. Answer each question to the best of your ability. The answer key is provided at the end.

**Time Limit**: 60 minutes (recommended)
**Passing Score**: 80% (20/25 correct)

## Questions

### Section 1: Kubernetes Architecture (Questions 1-6)

**Question 1**: Which Kubernetes component is responsible for scheduling Pods to nodes?
- A) kubelet
- B) kube-scheduler
- C) kube-controller-manager
- D) kube-proxy

**Question 2**: Where does Kubernetes store all cluster state and configuration?
- A) In memory on the API server
- B) In etcd
- C) In a relational database
- D) On each worker node

**Question 3**: What is the purpose of the kubelet?
- A) Schedule Pods to nodes
- B) Run controllers that manage cluster state
- C) Manage containers on a specific node
- D) Implement Service networking

**Question 4**: Which component implements Service load balancing on each node?
- A) kube-proxy
- B) kubelet
- C) Container runtime
- D) CoreDNS

**Question 5**: What communication protocol does the Kubernetes API Server use?
- A) gRPC
- B) REST (HTTP/HTTPS)
- C) WebSockets
- D) MQTT

**Question 6**: In Helm 3, where does Helm store release information?
- A) In a separate Tiller service
- B) In Kubernetes Secrets
- C) In etcd directly
- D) On the client machine only

### Section 2: Pods and Deployments (Questions 7-11)

**Question 7**: What is the smallest deployable unit in Kubernetes?
- A) Container
- B) Pod
- C) Deployment
- D) ReplicaSet

**Question 8**: How many containers can a Pod contain?
- A) Exactly one
- B) One or more
- C) At least two
- D) Up to five

**Question 9**: What happens when you delete a Deployment?
- A) Only the Deployment object is deleted
- B) The Deployment and ReplicaSets are deleted, but Pods remain
- C) The Deployment, ReplicaSets, and Pods are all deleted
- D) Nothing happens; Deployments cannot be deleted

**Question 10**: What is the purpose of a liveness probe?
- A) Determine if a container should receive traffic
- B) Determine if Kubernetes should restart a container
- C) Check if a container has started successfully
- D) Monitor resource usage

**Question 11**: In a rolling update with maxUnavailable=1 and maxSurge=1, starting with 3 replicas, what is the maximum number of Pods during the update?
- A) 3
- B) 4
- C) 5
- D) 6

### Section 3: Services and Networking (Questions 12-15)

**Question 12**: What is the default Service type in Kubernetes?
- A) NodePort
- B) LoadBalancer
- C) ClusterIP
- D) ExternalName

**Question 13**: How does a Service find its backend Pods?
- A) By IP address
- B) By name
- C) By label selectors
- D) By namespace

**Question 14**: What port range is used for NodePort services?
- A) 1-1024
- B) 8000-9000
- C) 30000-32767
- D) 40000-50000

**Question 15**: What is the full DNS name for a service named "api" in the "production" namespace?
- A) api.production
- B) api.production.svc
- C) api.production.svc.cluster.local
- D) production.api.cluster.local

### Section 4: Configuration and Storage (Questions 16-19)

**Question 16**: What is the difference between a ConfigMap and a Secret?
- A) Secrets are encrypted at rest, ConfigMaps are not (by default)
- B) ConfigMaps can be larger than Secrets
- C) Secrets can only store strings, ConfigMaps can store any data
- D) There is no difference; they're interchangeable

**Question 17**: What happens when you update a ConfigMap that's mounted as a volume in a running Pod?
- A) Pod automatically restarts
- B) File is updated in the container (eventually)
- C) Nothing; Pods don't see ConfigMap updates
- D) Container crashes

**Question 18**: What access mode allows multiple nodes to mount a volume for reading and writing?
- A) ReadWriteOnce (RWO)
- B) ReadOnlyMany (ROX)
- C) ReadWriteMany (RWX)
- D) ReadWriteMulti (RWM)

**Question 19**: What creates PersistentVolumes automatically when a PersistentVolumeClaim is created?
- A) kubelet
- B) StorageClass with dynamic provisioner
- C) PersistentVolume controller
- D) Volume plugin

### Section 5: Helm (Questions 20-22)

**Question 20**: What file in a Helm chart contains default configuration values?
- A) Chart.yaml
- B) values.yaml
- C) defaults.yaml
- D) config.yaml

**Question 21**: What is a Helm release?
- A) A version of Helm software
- B) An instance of a chart installed in a cluster
- C) A packaged Helm chart
- D) A Helm repository

**Question 22**: How do you roll back a Helm release to the previous version?
- A) `helm undo`
- B) `helm revert`
- C) `helm rollback`
- D) `helm restore`

### Section 6: Operations and Debugging (Questions 23-25)

**Question 23**: What kubectl command shows detailed information about a resource including events?
- A) kubectl get
- B) kubectl explain
- C) kubectl describe
- D) kubectl logs

**Question 24**: A Pod is in "CrashLoopBackOff" status. Which command shows why the container crashed?
- A) `kubectl logs <pod>`
- B) `kubectl logs <pod> --previous`
- C) `kubectl describe pod <pod>`
- D) Both B and C

**Question 25**: What does the command `kubectl top pods` display?
- A) The first few Pods in the list
- B) Current CPU and memory usage
- C) Pod priority levels
- D) Pods with most restarts

---

## Answer Key

### Section 1: Kubernetes Architecture
1. **B** - kube-scheduler is responsible for assigning Pods to nodes
2. **B** - etcd stores all cluster state using Raft consensus
3. **C** - kubelet manages containers and Pod lifecycle on each node
4. **A** - kube-proxy implements Service networking and load balancing
5. **B** - The API server uses REST (HTTP/HTTPS) for communication
6. **B** - Helm 3 stores releases as Secrets in Kubernetes

### Section 2: Pods and Deployments
7. **B** - Pod is the smallest deployable unit
8. **B** - Pods can contain one or more containers
9. **C** - Deleting a Deployment cascades to ReplicaSets and Pods
10. **B** - Liveness probes determine if a container should be restarted
11. **B** - maxSurge=1 allows up to 4 Pods (3 + 1), maxUnavailable=1 means at least 2 running

### Section 3: Services and Networking
12. **C** - ClusterIP is the default Service type
13. **C** - Services use label selectors to find Pods
14. **C** - NodePort uses port range 30000-32767
15. **C** - Full DNS name format: `<service>.<namespace>.svc.cluster.local`

### Section 4: Configuration and Storage
16. **A** - Secrets support encryption at rest, ConfigMaps do not (by default)
17. **B** - Mounted ConfigMaps are eventually updated in the container
18. **C** - ReadWriteMany (RWX) allows multi-node read-write access
19. **B** - StorageClass with dynamic provisioner automatically creates PVs

### Section 5: Helm
20. **B** - values.yaml contains default configuration values
21. **B** - A release is an instance of a chart installed in a cluster
22. **C** - `helm rollback` rolls back to previous version

### Section 6: Operations and Debugging
23. **C** - `kubectl describe` shows detailed information including events
24. **D** - Both `kubectl logs --previous` and `kubectl describe` help identify crash causes
25. **B** - `kubectl top pods` shows current CPU and memory usage

---

## Scoring Guide

- **25 correct (100%)**: Excellent! You have mastered Kubernetes fundamentals
- **23-24 correct (92-96%)**: Very good! Minor review recommended
- **20-22 correct (80-88%)**: Good! Review topics you missed
- **17-19 correct (68-76%)**: Fair! Review lectures and exercises
- **Below 17 (< 68%)**: Needs improvement! Review all material

## Review Recommendations by Section

**If you missed questions in Section 1 (Architecture)**:
- Re-read Lecture 01: Kubernetes Architecture
- Review the control plane and node components
- Understand the role of each component

**If you missed questions in Section 2 (Pods/Deployments)**:
- Re-read Lecture 02: Deploying Applications
- Complete Exercise 01 again
- Focus on Pod lifecycle and health probes

**If you missed questions in Section 3 (Services)**:
- Review Service types and DNS naming
- Practice creating Services
- Understand label selectors and endpoints

**If you missed questions in Section 4 (Config/Storage)**:
- Review ConfigMaps, Secrets, and Volumes
- Understand access modes and dynamic provisioning
- Practice mounting ConfigMaps and Secrets

**If you missed questions in Section 5 (Helm)**:
- Re-read Lecture 03: Helm
- Complete Exercise 02 again
- Practice with Helm commands

**If you missed questions in Section 6 (Operations)**:
- Re-read Lecture 04: Kubernetes Operations
- Complete Exercise 03 again
- Practice debugging workflows

---

## Additional Practice Questions

For more practice, try these bonus questions:

1. Explain the difference between Deployment and StatefulSet
2. Describe the complete flow of a Service request to a Pod
3. What happens during a rolling update with maxSurge=0 and maxUnavailable=1?
4. How would you debug a Pod that's stuck in "Pending"?
5. What's the difference between `kubectl apply` and `kubectl create`?
6. How do you update a Secret without restarting Pods?
7. What's the purpose of an Ingress resource?
8. How does Kubernetes handle node failures?
9. What's the difference between a DaemonSet and a Deployment?
10. How do you ensure two Pods never run on the same node?

---

## Next Steps

- **If you passed (80%+)**: Proceed to Module 007 (Advanced Kubernetes)
- **If you need review**: Focus on weak areas and retake quiz
- **All students**: Complete all three exercises if not done already
- **Extra credit**: Set up a multi-node cluster and practice all scenarios

## Feedback

Track your quiz results:

```
Date Taken: __________
Score: _____/25 (_____%)
Time Taken: _____ minutes

Areas to review:
- [ ] Architecture
- [ ] Pods and Deployments
- [ ] Services and Networking
- [ ] Configuration and Storage
- [ ] Helm
- [ ] Operations and Debugging

Notes:
_________________________________
_________________________________
_________________________________
```

---

**Congratulations on completing the Module 006 quiz!** This assessment validates your understanding of Kubernetes fundamentals essential for AI infrastructure work.

Keep practicing, and remember: hands-on experience is more valuable than memorizing answers!
