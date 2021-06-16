#ifndef GET_RODS_ENV_H__
#define GET_RODS_ENV_H__

#include "rodsDef.h"

typedef struct RodsEnvironment {
    char rodsUserName[NAME_LEN];
    char rodsHost[NAME_LEN];
    int  rodsPort;
    char rodsHome[MAX_NAME_LEN];
    char rodsCwd[MAX_NAME_LEN];
    char rodsAuthScheme[NAME_LEN];
    char rodsDefResource[NAME_LEN];
    char rodsZone[NAME_LEN];
    int rodsLogLevel;
    char rodsAuthFile[LONG_NAME_LEN];
    char rodsDebug[NAME_LEN];
    char rodsClientServerPolicy[ LONG_NAME_LEN ];
    char rodsClientServerNegotiation[ LONG_NAME_LEN ];

    // =-=-=-=-=-=-=-
    // client side options for encryption
    int  rodsEncryptionKeySize;
    int  rodsEncryptionSaltSize;
    int  rodsEncryptionNumHashRounds;
    char rodsEncryptionAlgorithm[ HEADER_TYPE_LEN ];

    // =-=-=-=-=-=-=-
    // client side options for hashing
    char rodsDefaultHashScheme[ NAME_LEN ];
    char rodsMatchHashPolicy[ NAME_LEN ];

    // =-=-=-=-=-=-=-
    // legacy ssl environment variables
    char irodsSSLCACertificatePath[MAX_NAME_LEN];
    char irodsSSLCACertificateFile[MAX_NAME_LEN];
    char irodsSSLVerifyServer[MAX_NAME_LEN];
    char irodsSSLCertificateChainFile[MAX_NAME_LEN];
    char irodsSSLCertificateKeyFile[MAX_NAME_LEN];
    char irodsSSLDHParamsFile[MAX_NAME_LEN];

    // =-=-=-=-=-=-=-
    // control plane parameters
    char irodsCtrlPlaneKey[MAX_NAME_LEN];
    int  irodsCtrlPlanePort;
    int  irodsCtrlPlaneEncryptionNumHashRounds;
    char irodsCtrlPlaneEncryptionAlgorithm[ HEADER_TYPE_LEN ];

    // =-=-=-=-=-=-=-
    // advanced settings
    int irodsMaxSizeForSingleBuffer;
    int irodsDefaultNumberTransferThreads;
    int irodsTransBufferSizeForParaTrans;
    int irodsConnectionPoolRefreshTime;

    // =-=-=-=-=-=-=-
    // override of plugin installation directory
    char irodsPluginHome[MAX_NAME_LEN];
} rodsEnv;

#ifdef __cplusplus
extern "C" {
#endif

int getRodsEnv( rodsEnv *myRodsEnv );

char *getRodsEnvFileName();
char *getRodsEnvAuthFileName();

int printRodsEnv( FILE* );

#ifdef __cplusplus

void _getRodsEnv( rodsEnv &myRodsEnv );
void _reloadRodsEnv( rodsEnv &myRodsEnv );

}
#endif
#endif // GET_RODS_ENV_H__
