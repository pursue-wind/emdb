deploy:
cd /data/event-tracker/event-tracker
1.chmod +x script.sh
2.start server
   ./script.sh start main
   ./script.sh start run_sync
   ./script.sh start all
3.stop server
   ./script.sh stop main
   ./script.sh stop run_sync
   ./script.sh stop all
4.restart server
   ./script.sh restart main
   ./script.sh restart run_sync
5.status
   ./script.sh status main
   ./script.sh status run_sync