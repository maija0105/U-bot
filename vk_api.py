<?php
class vk_public220904067{
    /**
     * Токен
     * @var string
     */
    private $token = '';
    private $v = '';
    /**
     * @param string $token Токен
     */
    public function __construct($token, $v){
        $this->token = $token;
        $this->v = $v;
    }
    /**
     * Отправить сообщение пользователю
     * @param int $sendID Идентификатор получателя
     * @param string $message Сообщение
     * @return mixed|null
     */
    public function sendDocMessage($sendID, $id_owner, $id_doc){
        if ($sendID != 0 and $sendID != '0') {
            return $this->request('messages.send',array('attachment'=>"doc". $id_owner . "_" . $id_doc,'user_id'=>$sendID));
        } else {
            return true;
        }
    }

    public function sendMessage($sendID,$message){
        if ($sendID != 0 and $sendID != '0') {
            return $this->request('messages.send',array('message'=>$message, 'peer_id'=>$sendID));
        } else {
            return true;
        }
    }

    public function sendOK(){
        echo 'ok';
        $response_length = ob_get_length();
        // check if fastcgi_finish_request is callable
        if (is_callable('fastcgi_finish_request')) {
            /*
             * This works in Nginx but the next approach not
             */
            session_write_close();
            fastcgi_finish_request();

            return;
        }

        ignore_user_abort(true);

        ob_start();
        $serverProtocole = filter_input(INPUT_SERVER, 'SERVER_PROTOCOL', FILTER_SANITIZE_STRING);
        header($serverProtocole.' 200 OK');
        header('Content-Encoding: none');
        header('Content-Length: '. $response_length);
        header('Connection: close');

        ob_end_flush();
        ob_flush();
        flush();
    }

    public function sendButton($sendID, $message, $gl_massiv = [], $one_time = False) {
        $buttons = [];
        $i = 0;
        foreach ($gl_massiv as $button_str) {
            $j = 0;
            foreach ($button_str as $button) {
                $color = $this->replaceColor($button[2]);
                $buttons[$i][$j]["action"]["type"] = "text";
                if ($button[0] != null)
                    $buttons[$i][$j]["action"]["payload"] = json_encode($button[0], JSON_UNESCAPED_UNICODE);
                $buttons[$i][$j]["action"]["label"] = $button[1];
                $buttons[$i][$j]["color"] = $color;
                $j++;
            }
            $i++;
        }
        $buttons = array(
            "one_time" => $one_time,
            "buttons" => $buttons);
        $buttons = json_encode($buttons, JSON_UNESCAPED_UNICODE);
        //echo $buttons;
        return $this->request('messages.send',array('message'=>$message, 'peer_id'=>$sendID, 'keyboard'=>$buttons));
    }

    public function sendDocuments($sendID, $selector = 'doc'){
        if ($selector == 'doc')
            return $this->request('docs.getMessagesUploadServer',array('type'=>'doc','peer_id'=>$sendID));
        else
            return $this->request('photos.getMessagesUploadServer',array('peer_id'=>$sendID));
    }

    public function saveDocuments($file, $titile){
        return $this->request('docs.save',array('file'=>$file, 'title'=>$titile));
    }

    public function savePhoto($photo, $server, $hash){
        return $this->request('photos.saveMessagesPhoto',array('photo'=>$photo, 'server'=>$server, 'hash' => $hash));
    }

    /**
     * Запрос к VK
     * @param string $method Метод
     * @param array $params Параметры
     * @return mixed|null
     */
    public function request($method,$params=array()){
        $url = 'https://api.vk.com/method/'.$method;
        $params['access_token']=$this->token;
        $params['v']=$this->v;
        if (function_exists('curl_init')) {
            $ch = curl_init();
            curl_setopt($ch, CURLOPT_HTTPHEADER, array(
                "Content-Type:multipart/form-data"
            ));
            curl_setopt($ch, CURLOPT_URL, $url);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
            curl_setopt($ch, CURLOPT_POSTFIELDS, $params);
            $result = json_decode(curl_exec($ch), True);
            curl_close($ch);
        } else {
            $result = json_decode(file_get_contents($url, true, stream_context_create(array(
                'http' => array(
                    'method'  => 'POST',
                    'header'  => "Content-type: application/x-www-form-urlencoded\r\n",
                    'content' => http_build_query($params)
                )
            ))), true);
        }
        if (isset($result['response']))
            return $result['response'];
        else
            return $result;
    }

    private function replaceColor($color) {
        switch ($color) {
            case 'red':
                $color = 'negative';
                break;
            case 'green':
                $color = 'positive';
                break;
            case 'white':
                $color = 'default';
                break;
            case 'blue':
                $color = 'primary';
                break;

            default:
                # code...
                break;
        }
        return $color;
    }

    private function sendFiles($url, $local_file_path, $type = 'file') {
        $post_fields = array(
            $type => new CURLFile(realpath($local_file_path))
        );

        $ch = curl_init();
        curl_setopt($ch, CURLOPT_HTTPHEADER, array(
            "Content-Type:multipart/form-data"
        ));
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $post_fields);
        $output = curl_exec($ch);
        return $output;
    }
    public function sendImage($id, $local_file_path)
    {
        $upload_url = $this->sendDocuments($id, 'photo')['upload_url'];

        $answer_vk = $this->sendFiles($upload_url, $local_file_path, 'photo');

        $upload_file = $this->savePhoto($answer_vk[0]['photo'], $answer_vk[0]['server'], $answer_vk[0]['hash']);

        $this->request('messages.send', array('attachment' => "photo" . $upload_file[0]['owner_id'] . "_" . $upload_file[0]['id'], 'peer_id' => $id));

        return 1;
    }
    public function isChatAdmin($peer_id)
    {
      $check_error = $this->request('messages.getConversationMembers', ['peer_id' => $peer_id]);
      if(!empty($check_error['error'])) {
        if($check_error['error']['error_code'] == 917){
          return false;
        }
      }
      return true;
    }
    public function registrationUser($id)
    {
      $get_user = R::findOne('users', 'user_id = ?', [$id]);
      if(!$get_user){
        $userInfo = $this->request("users.get", ["user_ids" => $id, "fields" => ('city, sex')]); // Делаем запрос к вк
        $first_name = $userInfo[0]['first_name']; // Вывели из ответа имя
        $last_name = $userInfo[0]['last_name']; // Вывели из ответа фамилию
        $sex = $userInfo[0]['sex']; // Вывели из ответа пол
        $city = $userInfo[0]['city']['title']; // Вывели из ответа город

        $NewUser = R::dispense("users");
        $NewUser->user_id = $id;
        $NewUser->first_name = $first_name;
        $NewUser->last_name = $last_name;
        $NewUser->city = $city;
        $NewUser->sex = $sex;
        $NewUser->nick_name = "{$first_name} " . "{$last_name}";
        $NewUser->balance = 0;
        R::store($NewUser);
      }
    }
    public function registrationChatSettings($peer_id)
    {
      $get_members = $this->request('messages.getConversationMembers', ['peer_id' => $peer_id]); // Получили список пользователей беседы
      foreach ($get_members['profiles'] as $member) { // Прошли по массиву для регистрации пользователей по их id
        $user_id = $member['id']; // Получили id пользоавтеля
        $this->registrationUser($user_id); // Отправили этот id для прошлой функции (регистрации)
      }
      if(!R::findOne('settings', 'peer_id = ?', [$peer_id])){ // Проверяем на наличие регистрации настроек беседы в базе
        $chat_data = $this->request('messages.getConversationsById', ['peer_ids' => $peer_id, 'extended' => 0]); // Получили информацию о беседе
        $chat = R::dispense("settings"); // Регистрируем в базе
        $chat->peer_id = $peer_id;
        $chat->title = $chat_data['items'][0]['chat_settings']['title']; // Название беседы
        $chat->edit_title = 0;
        $chat->owner_id = $chat_data['items'][0]['chat_settings']['owner_id']; // Создатель беседы
        $chat->users = $chat_data['items'][0]['chat_settings']['members_count']; // Кол-во участников беседы
        $chat->auto_kick = 0;
        R::store($chat);
      }
      $this->sendMessage($peer_id, "Беседа успешно зарегистрирована 😉");
    }
}
