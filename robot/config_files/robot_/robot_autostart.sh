# Iniciando servicos do robo.
##

# Comunicando inicio da inicializacao.
espeak robot
sleep 2

# Servico do Veiculo
export PYTHONPATH="/usr/local/lib/python2.6/dist-packages:$PYTHONPATH"
cd $HOME/NetBeansProjects/wsrest_veiculo/src/veiculo/
nohup ./main.py 8080 > $HOME/robot_/veiculo.log 2>&1 &

# Servico de Audicao
cd $HOME/NetBeansProjects/wsrest_audicao/src/audicao/
nohup ./wsrest_audicao.py 8090 > $HOME/robot_/audicao.log 2>&1 &

# Servico face detect
#cd $HOME/NetBeansProjects/wsrest_face_detect/src/face_detect/
#nohup $HOME/NetBeansProjects/wsrest_face_detect/src/face_detect/wsrest_face_detect.py 8091 > $HOME/robot_/face_detect.log 2>&1 &

# Servico de comando de voz
cd $HOME/NetBeansProjects/wsrest_voice_command/src/voice_command/
nohup ./wsrest_voice_command.py 8092 > $HOME/robot_/voice_command.log 2>&1 &

# Servico fuzzy follow
cd $HOME/NetBeansProjects/wsrest_fuzzy_follow/src/fuzzy_follow/
nohup ./wsrest_fuzzy_follow.py 8093 > $HOME/robot_/fuzzy_follow.log 2>&1 &

# Servico kinect
cd $HOME/NetBeansProjects/wsrest_kinect/src/kinect/
nohup ./wsrest_kinect.py 8094 > $HOME/robot_/kinect.log 2>&1 &

# Servico Tts
cd $HOME/NetBeansProjects/wsrest_tts/src/tts/
nohup ./wsrest_tts.py 8096 > $HOME/robot_/tts.log 2>&1 &

# Alterando permissoes na porta serial do gps.
#sudo chmod 666 /dev/ttyUSB0

# Inicializando servico de audicao.
sleep 50
nohup wget http://localhost:8090 > $HOME/robot_/wget.log 2>&1 &
sleep 10


# Comunicando final da inicializacao.
espeak -vpt pronto

