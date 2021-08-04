#ifndef IRODS_REGISTER_PHYSICAL_PATH_H
#define IRODS_REGISTER_PHYSICAL_PATH_H

/// \file

struct RcComm;
struct DataObjInp;

#ifdef __cplusplus
extern "C" {
#endif

/// \brief Registers a physical path as a replica of an iRODS data object.
///
/// \parblock
/// _in must contain the FILE_PATH_KW which specifies the physical path being registered.
///
/// _json_output contains the information for the registered replica. This includes the
/// information generated by the database which is not known to the caller beforehand (e.g.
/// data ID). The serialization used is irods::experimental::replica_proxy::to_json. There
/// are free functions available there which deserialize the data to the DataObjInfo struct.
/// \endparblock
///
/// \param[in]  _comm        A pointer to an RcComm.
/// \param[in]  _in          A DataObjInp which describes the replica and path to register.
/// \param[out] _json_output A JSON string which describes the replica which was registered.
///
/// \return An integer.
/// \retval 0        On success.
/// \retval non-zero On failure.
///
/// \since 4.2.11
int rc_register_physical_path(struct RcComm* _comm, struct DataObjInp* _in, char** _json_output);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // IRODS_REGISTER_PHYSICAL_PATH_H

