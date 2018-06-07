CMAKE_MINIMUM_REQUIRED(VERSION 2.6 FATAL_ERROR)
CMAKE_POLICY(VERSION 2.6)

FILE(GLOB src *.cc *.h)
FILE(GLOB luasrc *.lua)
SET(luasrc ${luasrc} alelua.inl)

MESSAGE(STATUS "CMAKE_INSTALL_PREFIX ${CMAKE_INSTALL_PREFIX}")
MESSAGE(STATUS "TORCH_INSTALL_PREFIX ${TORCH_INSTALL_PREFIX}")
MESSAGE(STATUS "LUAROCKS_INSTALL_PREFIX ${LUAROCKS_INSTALL_PREFIX}")

IF ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
    MESSAGE(STATUS "Using Clang")
    SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3")        ## Optimize
    SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -ftemplate-depth=1024")
    MESSAGE(STATUS "FLAGS ${CMAKE_CXX_FLAGS}")
# Using GCC.
ELSEIF ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
    MESSAGE(STATUS "Using GCC")
    SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3")        ## Optimize
    SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O3")        ## Optimize
    MESSAGE(STATUS "FLAGS ${CMAKE_CXX_FLAGS}")
# Using Intel C++.
ELSEIF ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Intel")
    MESSAGE(STATUS "Using Intel C++")
# Using Visual Studio C++.
ELSEIF ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "MSVC")
    MESSAGE(STATUS "Using Visual Studio C++")
ENDIF()


# We are building alelualib.
# We specify the paths to ALE includes and libale.
# INCLUDE_DIRECTORIES(${Torch_SOURCE_INCLUDES})
find_path(SAFARI_INCLUDE_DIR safari /ale_interface.hpp
          HINTS 
          ${TORCH_INSTALL_PREFIX}/include
          ${CMAKE_INSTALL_PREFIX}/include
          ${CMAKE_INSTALL_PREFIX}/../../../../../include
          ${LUAROCKS_INSTALL_PREFIX}/../../../../../include
          PATH_SUFFIXES include)

find_path(SAFARI_LIBRARY_DIR NAMES safari  libsafari .a
          HINTS 
          ${TORCH_INSTALL_PREFIX}/lib 
          ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/../../../../../lib 
          ${LUAROCKS_INSTALL_PREFIX}/../../../../../lib)

find_library(SAFARI_LIBRARY NAMES safari  libsafari .a
          HINTS 
          ${TORCH_INSTALL_PREFIX}/lib 
          ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/../../../../../lib 
          ${LUAROCKS_INSTALL_PREFIX}/../../../../../lib)

IF(NOT(SAFARI_INCLUDE_DIR))
  MESSAGE(ERROR "Could not find Safari  include location")
ENDIF()

IF(NOT(SAFARI_LIBRARY_DIR))
  MESSAGE(ERROR "Could not find Safari  library")
ENDIF()

IF(NOT(SAFARI_LIBRARY))
  MESSAGE(ERROR "Could not find Safari  library")
ENDIF()

SET(INCDIR "${SAFARI_INCLUDE_DIR}")
SET(LIBDIR "${SAFARI_LIBRARY_DIR}")

INCLUDE_DIRECTORIES("${INCDIR}")
LINK_DIRECTORIES("${LIBDIR}")

ADD_TORCH_PACKAGE(alelua "${src}" "${luasrc}" "ALE Wrapper")
TARGET_LINK_LIBRARIES(alelua ${SAFARI_LIBRARY})

# INCLUDE_DIRECTORIES(../../xiborg/safari )
# LINK_DIRECTORIES(${CMAKE_CURRENT_SOURCE_DIR}/../../xiborg/safari /build)
# ADD_LIBRARY(alelualib SHARED ${libsrc})
# TARGET_LINK_LIBRARIES(alelualib safari  z)
