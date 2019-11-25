<?php
set_time_limit(0);
date_default_timezone_set('UTC');
require __DIR__.'/vendor/autoload.php';
/////// CONFIG ///////
$username            = $argv[1];
$password            = $argv[2];
$debug = true;
$truncatedDebug = false;
//////////////////////
/////// MEDIA ////////
$photoFilename = $argv[3];
$captionText = implode(" " ,array_slice($argv, 4));
//////////////////////
$ig = new \InstagramAPI\Instagram($debug, $truncatedDebug);
try {
    $ig->login($username, $password);
} catch (\Exception $e) {
    echo 'LOGIN EXCEPTION: '.$e->getMessage()."\n";
    exit(0);
}
try {
    $photo = new \InstagramAPI\Media\Photo\InstagramPhoto($photoFilename);
    $ig->timeline->uploadPhoto($photo->getFile(), ['caption' => $captionText]);
} catch (\Exception $e) {
    echo 'Something went wrong: '.$e->getMessage()."\n";
}