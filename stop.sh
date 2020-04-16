
pid=$(ps aux | grep "python nullbot/bot.py" | grep -v grep | awk '{print $2}')
echo $pid
kill $pid