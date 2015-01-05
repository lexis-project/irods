/*** Copyright (c), The Regents of the University of California            ***
 *** For more information please refer to files in the COPYRIGHT directory ***/
/* dataObjPhymv.h - This dataObj may be generated by a program or script
 */

#ifndef DATA_OBJ_PHYMV_HPP
#define DATA_OBJ_PHYMV_HPP

/* This is a Object File I/O API call */

#include "rods.hpp"
#include "rcMisc.hpp"
#include "procApiRequest.hpp"
#include "apiNumber.hpp"
#include "initServer.hpp"
#include "dataObjWrite.hpp"
#include "dataObjClose.hpp"
#include "dataCopy.hpp"

#if defined(RODS_SERVER)
#define RS_DATA_OBJ_PHYMV rsDataObjPhymv
/* prototype for the server handler */
int
rsDataObjPhymv( rsComm_t *rsComm, dataObjInp_t *dataObjInp,
                transferStat_t **transferStat );
int
_rsDataObjPhymv( rsComm_t *rsComm, dataObjInp_t *dataObjInp,
                 dataObjInfo_t *srcDataObjInfoHead, const char *resc_name,
                 transferStat_t *transStat, int multiCopyFlag );
#else
#define RS_DATA_OBJ_PHYMV NULL
#endif

#ifdef __cplusplus
extern "C" {
#endif
/* prototype for the client call */
/* rcDataObjPhymv - Move an iRODS data object from one resource to another.
 * Input -
 *   rcComm_t *conn - The client connection handle.
 *   dataObjInp_t *dataObjInp - generic dataObj input. Relevant items are:
 *      objPath - the path of the data object to be moved.
 *      condInput - condition input (optional).
 *	    ADMIN_KW - Admin moving other users' files.
 *          REPL_NUM_KW  - "value" = The replica number of the copy to
 *              be moved.
 *	    RESC_NAME_KW - "value" = The resource of the physical data to
 *	        be moved.
 *          DEST_RESC_NAME_KW - "value" = The destination Resource of the move.
 *
 * OutPut -
 *   int status of the operation - >= 0 ==> success, < 0 ==> failure.
 */

int
rcDataObjPhymv( rcComm_t *conn, dataObjInp_t *dataObjInp );
int
_rcDataObjPhymv( rcComm_t *conn, dataObjInp_t *dataObjInp,
                 transferStat_t **transferStat );
#ifdef __cplusplus
}
#endif
#endif	/* DATA_OBJ_PHYMV_H */
