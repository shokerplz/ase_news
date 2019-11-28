<?php
use InstagramAPI\Client;
use InstagramAPI\Constants;
use InstagramAPI\Request\Metadata\Internal as InternalMetadata;
use InstagramAPI\Utils;
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

class ExtInternal extends \InstagramAPI\Request\Internal {
    public function uploadPhotoData(
        $targetFeed,
        InternalMetadata $internalMetadata)
    {
        // Make sure we disallow some feeds for this function.
        if ($targetFeed === Constants::FEED_DIRECT) {
            throw new \InvalidArgumentException(sprintf('Bad target feed "%s".', $targetFeed));
        }

        // Make sure we have photo details.
        if ($internalMetadata->getPhotoDetails() === null) {
            throw new \InvalidArgumentException('Photo details are missing from the internal metadata.');
        }

        try {
            // Upload photo file with one of our photo uploaders.
            $this->_uploadResumablePhoto($targetFeed, $internalMetadata);
        } catch (InstagramException $e) {
            // Pass Instagram's error as is.
            throw $e;
        } catch (\Exception $e) {
            // Wrap runtime errors.
            throw new UploadFailedException(
                sprintf(
                    'Upload of "%s" failed: %s',
                    $internalMetadata->getPhotoDetails()->getBasename(),
                    $e->getMessage()
                ),
                $e->getCode(),
                $e
            );
        }
    }
}

$ig = new \InstagramAPI\Instagram($debug, $truncatedDebug, [
    'storage'     => 'sqlite',
    'dbfilename'  => 'instagram.sqlite',
    'dbtablename' => 'instagram_sessions',
]);
try {
    $ig->login($username, $password);
    $internal = new ExtInternal($ig);
} catch (\Exception $e) {
    echo 'LOGIN EXCEPTION: '.$e->getMessage()."\n";
    exit(0);
}

try {
    $photo = new \InstagramAPI\Media\Photo\InstagramPhoto($photoFilename);
    $internalMetadata = new InternalMetadata(Utils::generateUploadId(true));
    $targetFeed = Constants::FEED_TIMELINE;
    try {
        if ($internalMetadata->getPhotoDetails() === null) {
            $internalMetadata->setPhotoDetails($targetFeed, $photoFilename);
        }
    } catch (\Exception $e) {
        throw new \InvalidArgumentException(
            sprintf('Failed to get photo details: %s', $e->getMessage()),
            $e->getCode(),
            $e
        );
    }
    $internal->uploadPhotoData($targetFeed, $internalMetadata);
    $configure = $internal->configureSinglePhoto($targetFeed, $internalMetadata, ['caption' => $captionText]);
    return $configure;

} catch (\Exception $e) {
    echo 'Something went wrong: '.$e->getMessage()."\n";
}

