// Code generated by protoc-gen-go. DO NOT EDIT.
// source: bad.proto

package schema_proto2

import proto "github.com/golang/protobuf/proto"
import fmt "fmt"
import math "math"

// Reference imports to suppress errors if they are not otherwise used.
var _ = proto.Marshal
var _ = fmt.Errorf
var _ = math.Inf

// This is a compile-time assertion to ensure that this generated file
// is compatible with the proto package it is being compiled against.
// A compilation error at this line likely means your copy of the
// proto package needs to be updated.
const _ = proto.ProtoPackageIsVersion2 // please upgrade the proto package

// Should fail when encountering custom default values.
type BadWithDefaults struct {
	Text                 *string  `protobuf:"bytes,1,opt,name=text,def=N/A" json:"text,omitempty"`
	XXX_NoUnkeyedLiteral struct{} `json:"-"`
	XXX_unrecognized     []byte   `json:"-"`
	XXX_sizecache        int32    `json:"-"`
}

func (m *BadWithDefaults) Reset()         { *m = BadWithDefaults{} }
func (m *BadWithDefaults) String() string { return proto.CompactTextString(m) }
func (*BadWithDefaults) ProtoMessage()    {}
func (*BadWithDefaults) Descriptor() ([]byte, []int) {
	return fileDescriptor_bad_c5d891dc6e0e10ff, []int{0}
}
func (m *BadWithDefaults) XXX_Unmarshal(b []byte) error {
	return xxx_messageInfo_BadWithDefaults.Unmarshal(m, b)
}
func (m *BadWithDefaults) XXX_Marshal(b []byte, deterministic bool) ([]byte, error) {
	return xxx_messageInfo_BadWithDefaults.Marshal(b, m, deterministic)
}
func (dst *BadWithDefaults) XXX_Merge(src proto.Message) {
	xxx_messageInfo_BadWithDefaults.Merge(dst, src)
}
func (m *BadWithDefaults) XXX_Size() int {
	return xxx_messageInfo_BadWithDefaults.Size(m)
}
func (m *BadWithDefaults) XXX_DiscardUnknown() {
	xxx_messageInfo_BadWithDefaults.DiscardUnknown(m)
}

var xxx_messageInfo_BadWithDefaults proto.InternalMessageInfo

const Default_BadWithDefaults_Text string = "N/A"

func (m *BadWithDefaults) GetText() string {
	if m != nil && m.Text != nil {
		return *m.Text
	}
	return Default_BadWithDefaults_Text
}

// Should fail when encountering required fields.
type BadWithRequirements struct {
	Text                 *string  `protobuf:"bytes,1,req,name=text" json:"text,omitempty"`
	XXX_NoUnkeyedLiteral struct{} `json:"-"`
	XXX_unrecognized     []byte   `json:"-"`
	XXX_sizecache        int32    `json:"-"`
}

func (m *BadWithRequirements) Reset()         { *m = BadWithRequirements{} }
func (m *BadWithRequirements) String() string { return proto.CompactTextString(m) }
func (*BadWithRequirements) ProtoMessage()    {}
func (*BadWithRequirements) Descriptor() ([]byte, []int) {
	return fileDescriptor_bad_c5d891dc6e0e10ff, []int{1}
}
func (m *BadWithRequirements) XXX_Unmarshal(b []byte) error {
	return xxx_messageInfo_BadWithRequirements.Unmarshal(m, b)
}
func (m *BadWithRequirements) XXX_Marshal(b []byte, deterministic bool) ([]byte, error) {
	return xxx_messageInfo_BadWithRequirements.Marshal(b, m, deterministic)
}
func (dst *BadWithRequirements) XXX_Merge(src proto.Message) {
	xxx_messageInfo_BadWithRequirements.Merge(dst, src)
}
func (m *BadWithRequirements) XXX_Size() int {
	return xxx_messageInfo_BadWithRequirements.Size(m)
}
func (m *BadWithRequirements) XXX_DiscardUnknown() {
	xxx_messageInfo_BadWithRequirements.DiscardUnknown(m)
}

var xxx_messageInfo_BadWithRequirements proto.InternalMessageInfo

func (m *BadWithRequirements) GetText() string {
	if m != nil && m.Text != nil {
		return *m.Text
	}
	return ""
}

// Adding extensions to a proto is also illegal.
type BadWithExtensions struct {
	Text                         *string  `protobuf:"bytes,3,opt,name=text" json:"text,omitempty"`
	XXX_NoUnkeyedLiteral         struct{} `json:"-"`
	proto.XXX_InternalExtensions `json:"-"`
	XXX_unrecognized             []byte `json:"-"`
	XXX_sizecache                int32  `json:"-"`
}

func (m *BadWithExtensions) Reset()         { *m = BadWithExtensions{} }
func (m *BadWithExtensions) String() string { return proto.CompactTextString(m) }
func (*BadWithExtensions) ProtoMessage()    {}
func (*BadWithExtensions) Descriptor() ([]byte, []int) {
	return fileDescriptor_bad_c5d891dc6e0e10ff, []int{2}
}

var extRange_BadWithExtensions = []proto.ExtensionRange{
	{Start: 100, End: 199},
}

func (*BadWithExtensions) ExtensionRangeArray() []proto.ExtensionRange {
	return extRange_BadWithExtensions
}
func (m *BadWithExtensions) XXX_Unmarshal(b []byte) error {
	return xxx_messageInfo_BadWithExtensions.Unmarshal(m, b)
}
func (m *BadWithExtensions) XXX_Marshal(b []byte, deterministic bool) ([]byte, error) {
	return xxx_messageInfo_BadWithExtensions.Marshal(b, m, deterministic)
}
func (dst *BadWithExtensions) XXX_Merge(src proto.Message) {
	xxx_messageInfo_BadWithExtensions.Merge(dst, src)
}
func (m *BadWithExtensions) XXX_Size() int {
	return xxx_messageInfo_BadWithExtensions.Size(m)
}
func (m *BadWithExtensions) XXX_DiscardUnknown() {
	xxx_messageInfo_BadWithExtensions.DiscardUnknown(m)
}

var xxx_messageInfo_BadWithExtensions proto.InternalMessageInfo

func (m *BadWithExtensions) GetText() string {
	if m != nil && m.Text != nil {
		return *m.Text
	}
	return ""
}

func init() {
	proto.RegisterType((*BadWithDefaults)(nil), "schema.proto2.BadWithDefaults")
	proto.RegisterType((*BadWithRequirements)(nil), "schema.proto2.BadWithRequirements")
	proto.RegisterType((*BadWithExtensions)(nil), "schema.proto2.BadWithExtensions")
}

func init() { proto.RegisterFile("bad.proto", fileDescriptor_bad_c5d891dc6e0e10ff) }

var fileDescriptor_bad_c5d891dc6e0e10ff = []byte{
	// 142 bytes of a gzipped FileDescriptorProto
	0x1f, 0x8b, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0xff, 0xe2, 0xe2, 0x4c, 0x4a, 0x4c, 0xd1,
	0x2b, 0x28, 0xca, 0x2f, 0xc9, 0x17, 0xe2, 0x2d, 0x4e, 0xce, 0x48, 0xcd, 0x4d, 0x84, 0xf0, 0x8c,
	0x94, 0xb4, 0xb8, 0xf8, 0x9d, 0x12, 0x53, 0xc2, 0x33, 0x4b, 0x32, 0x5c, 0x52, 0xd3, 0x12, 0x4b,
	0x73, 0x4a, 0x8a, 0x85, 0xc4, 0xb9, 0x58, 0x4a, 0x52, 0x2b, 0x4a, 0x24, 0x18, 0x15, 0x18, 0x35,
	0x38, 0xad, 0x98, 0xfd, 0xf4, 0x1d, 0x83, 0xc0, 0x02, 0x4a, 0x9a, 0x5c, 0xc2, 0x50, 0xb5, 0x41,
	0xa9, 0x85, 0xa5, 0x99, 0x45, 0xa9, 0xb9, 0xa9, 0x79, 0x25, 0xc5, 0x42, 0x42, 0x70, 0xf5, 0x4c,
	0x1a, 0x9c, 0x50, 0xa5, 0x7a, 0x5c, 0x82, 0x50, 0xa5, 0xae, 0x15, 0x25, 0xa9, 0x79, 0xc5, 0x99,
	0xf9, 0x79, 0x08, 0x85, 0xcc, 0x20, 0x83, 0x21, 0x0a, 0xb5, 0x58, 0x39, 0x52, 0x04, 0x4e, 0x30,
	0x02, 0x02, 0x00, 0x00, 0xff, 0xff, 0xa7, 0x5b, 0xf9, 0x4b, 0xa1, 0x00, 0x00, 0x00,
}