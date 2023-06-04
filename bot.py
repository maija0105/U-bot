<?php
require 'db.php';
include "vk1.a.dU4lN6mgxOwhdZkoTZhT-Tu4875GTRlGIXpfN1L0jPU0L-w-yDB35rBGe7yIkI7m3BDJKYRL_ECaIUaPw-MbdYeaWtpVcRAk7-ZKVifdlJgiDVDBBo-h25XoZapPi2jJ0jo1px12sb1aJvd8FWOXawD6zpcxKFZbwOHLrDxIzDKCrzM-LA5ReagZxh4-AlkUDpjfxL57MSQFuBKE7JdnQw.php";

const VK_KEY = "Токен сообщества";
const ACCESS_KEY = "Токен подтверждения";
const VERSION = "5.81";

$vk = new vk_api(VK_KEY, VERSION);
$data = json_decode(file_get_contents('php://input'));
//print_r($data);
if ($data->type == 'confirmation') {
    exit(ACCESS_KEY);
}
$vk->sendOK();
// ---------- Переменные ----------
$peer_id = $data->object->peer_id;
$id = $data->object->from_id;
$chat_id = $peer_id - 2000000000;
// ---------- Сообщение ----------
$message = $data->object->text;
$messages = explode(" ", $message);
$cmd = mb_strtolower(str_replace(array("/", "!"), "", $messages[0]));
$args = array_slice($messages, 1);
$reason = implode(" ", $args);
// ---------- Другое ----------
$reply_message = $data->object->reply_message;
$reply_author = $data->object->reply_message->from_id;
$chat_act = $data->object->action;
$fwd_messages = $object['fwd_messages'];
if(empty($fwd_messages) && !empty($reply_message)) {
  array_push($fwd_messages, $reply_message);
}
if(empty($reply_message) && !empty($fwd_messages)) {
  $reply_message = $fwd_messages[0];
}
if ( !R::testConnection() )
{
    $vk->sendMessage($peer_id, "Нет соединения с базой данных, обратитесь к администраторам ");
    exit;
}
if ($data->type == 'message_new') {
  if($chat_id > 0){//Проверка на админкиу в чате
    if(!$vk->isChatAdmin($peer_id)){
      $vk->sendMessage($peer_id, "⚠ Мне необходимы права администратора ⚠");
      exit;
    }else{// проверка на регистрацию чата
      $chat = R::findOne('settings', 'peer_id = ?', [$peer_id]);
      if(!$chat){
        $vk->registrationChat($peer_id);
      }
    }
  }
  $chatSettings = R::findOne('settings', 'peer_id = ?', [$peer_id]);
  $actionUser = $chat_act->member_id;
  if($chat_act->type == 'chat_invite_user' || $chat_act->type == 'chat_invite_user_by_link'){ // Новый пользователь
    $checkUserChat = R::findOne("{$peer_id}", 'user_id = ?', [$actionUser]);
    $ChatSettings->users = $ChatSettings->users + 1;
    R::store($ChatSettings);
    $vk->registrationUser($id);
  }elseif($chat_act->type == 'chat_kick_user'){// проверка на исключение пользователя
    $kick = $vk->request('messages.removeChatUser', ['chat_id' => $chat_id, 'member_id' => $actionUser]);
    $ChatSettings->users = $ChatSettings->users - 1;
    R::store($ChatSettings);
  }elseif($chat_act->type == 'chat_title_update'){
    $ChatSettings->title = $chat_act->text;
    R::store($ChatSettings);
    $vk->sendMessage($peer_id, "💬 Новое название чата: {$chat_act->text}");
  }
}
/*
elseif(in_array($cmd, ['', ''])){

}
*/
