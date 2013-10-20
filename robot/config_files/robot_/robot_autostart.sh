# Iniciando servicos do robo.
##

# Comunicando inicio da inicializacao.
espeak -vpt robor
sleep 2

# Servico do Veiculo
export PYTHONPATH="/usr/local/lib/python2.6/dist-packages:$PYTHONPATH"
#cd $HOME/NetBeansProjects/wsrest_veiculo/src/veiculo/
#sudo nohup ./wsrest_veiculo.py 8080 > $HOME/robot_/logs/wsrest_veiculo.log 2>&1 &

# Servico de Audicao
cd $HOME/NetBeansProjects/wsrest_listen/src/listen/
nohup ./wsrest_listen.py 8090 > $HOME/robot_/logs/listen.log 2>&1 &

# Servico face detect
cd $HOME/NetBeansProjects/wsrest_face_detect/src/face_detect/
nohup $HOME/NetBeansProjects/wsrest_face_detect/src/face_detect/wsrest_face_detect_kinect.py 8091 > $HOME/robot_/logs/face_detect.log 2>&1 &

# Servico de GPS
cd $HOME/NetBeansProjects/wsrest_gps/src/gps/
nohup ./wsrest_gps.py 8092 > $HOME/robot_/logs/gps.log 2>&1 &

# Servico fuzzy follow
cd $HOME/NetBeansProjects/wsrest_fuzzy_follow/src/fuzzy_follow/
nohup ./wsrest_fuzzy_follow.py 8093 > $HOME/robot_/logs/fuzzy_follow.log 2>&1 &

# Servico kinect
cd $HOME/NetBeansProjects/wsrest_kinect/src/kinect/
nohup ./wsrest_kinect.py 8094 > $HOME/robot_/logs/kinect.log 2>&1 &

# Servico tts
cd $HOME/NetBeansProjects/wsrest_tts/src/tts/
nohup ./wsrest_tts.py 8096 > $HOME/robot_/logs/tts.log 2>&1 &

# Servico STM
cd $HOME/NetBeansProjects/wsrest_stm/src/stm/
nohup ./wsrest_stm.py 8098 > $HOME/robot_/logs/stm.log 2>&1 &


# Alterando permissoes na porta serial do gps.
#sudo chmod 666 /dev/ttyUSB0

# Inicializando servico de audicao.
sleep 50
nohup wget http://localhost:8090 > $HOME/robot_/logs/wget.log 2>&1 &
sleep 10


# Carregando "agentes"

# Runaway
#cd $HOME/NetBeansProjects/agent_runaway/src/runaway/
#nohup ./agent_runaway.py 8101 > $HOME/robot_/logs/runaway.log 2>&1 &

# Look at me
cd $HOME/NetBeansProjects/agent_look_at_me/src/look_at_me/
nohup ./agent_look_at_me.py 8103 > $HOME/robot_/logs/look_at_me.log 2>&1 &

# Voice Command
cd $HOME/NetBeansProjects/agent_voice_command/src/voice_command/
nohup ./agent_voice_command.py 8104 > $HOME/robot_/logs/voice_command.log 2>&1 &


# Comunicando final da inicializacao.
espeak -vpt pronto

