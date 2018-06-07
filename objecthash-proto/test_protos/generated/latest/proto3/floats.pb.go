// Code generated by protoc-gen-go. DO NOT EDIT.
// source: floats.proto

package schema_proto3

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

type DoubleMessage struct {
	Value                float64   `protobuf:"fixed64,1,opt,name=value" json:"value,omitempty"`
	Values               []float64 `protobuf:"fixed64,2,rep,packed,name=values" json:"values,omitempty"`
	XXX_NoUnkeyedLiteral struct{}  `json:"-"`
	XXX_unrecognized     []byte    `json:"-"`
	XXX_sizecache        int32     `json:"-"`
}

func (m *DoubleMessage) Reset()         { *m = DoubleMessage{} }
func (m *DoubleMessage) String() string { return proto.CompactTextString(m) }
func (*DoubleMessage) ProtoMessage()    {}
func (*DoubleMessage) Descriptor() ([]byte, []int) {
	return fileDescriptor_floats_f5de057cb502e988, []int{0}
}
func (m *DoubleMessage) XXX_Unmarshal(b []byte) error {
	return xxx_messageInfo_DoubleMessage.Unmarshal(m, b)
}
func (m *DoubleMessage) XXX_Marshal(b []byte, deterministic bool) ([]byte, error) {
	return xxx_messageInfo_DoubleMessage.Marshal(b, m, deterministic)
}
func (dst *DoubleMessage) XXX_Merge(src proto.Message) {
	xxx_messageInfo_DoubleMessage.Merge(dst, src)
}
func (m *DoubleMessage) XXX_Size() int {
	return xxx_messageInfo_DoubleMessage.Size(m)
}
func (m *DoubleMessage) XXX_DiscardUnknown() {
	xxx_messageInfo_DoubleMessage.DiscardUnknown(m)
}

var xxx_messageInfo_DoubleMessage proto.InternalMessageInfo

func (m *DoubleMessage) GetValue() float64 {
	if m != nil {
		return m.Value
	}
	return 0
}

func (m *DoubleMessage) GetValues() []float64 {
	if m != nil {
		return m.Values
	}
	return nil
}

type FloatMessage struct {
	Value                float32   `protobuf:"fixed32,1,opt,name=value" json:"value,omitempty"`
	Values               []float32 `protobuf:"fixed32,2,rep,packed,name=values" json:"values,omitempty"`
	XXX_NoUnkeyedLiteral struct{}  `json:"-"`
	XXX_unrecognized     []byte    `json:"-"`
	XXX_sizecache        int32     `json:"-"`
}

func (m *FloatMessage) Reset()         { *m = FloatMessage{} }
func (m *FloatMessage) String() string { return proto.CompactTextString(m) }
func (*FloatMessage) ProtoMessage()    {}
func (*FloatMessage) Descriptor() ([]byte, []int) {
	return fileDescriptor_floats_f5de057cb502e988, []int{1}
}
func (m *FloatMessage) XXX_Unmarshal(b []byte) error {
	return xxx_messageInfo_FloatMessage.Unmarshal(m, b)
}
func (m *FloatMessage) XXX_Marshal(b []byte, deterministic bool) ([]byte, error) {
	return xxx_messageInfo_FloatMessage.Marshal(b, m, deterministic)
}
func (dst *FloatMessage) XXX_Merge(src proto.Message) {
	xxx_messageInfo_FloatMessage.Merge(dst, src)
}
func (m *FloatMessage) XXX_Size() int {
	return xxx_messageInfo_FloatMessage.Size(m)
}
func (m *FloatMessage) XXX_DiscardUnknown() {
	xxx_messageInfo_FloatMessage.DiscardUnknown(m)
}

var xxx_messageInfo_FloatMessage proto.InternalMessageInfo

func (m *FloatMessage) GetValue() float32 {
	if m != nil {
		return m.Value
	}
	return 0
}

func (m *FloatMessage) GetValues() []float32 {
	if m != nil {
		return m.Values
	}
	return nil
}

func init() {
	proto.RegisterType((*DoubleMessage)(nil), "schema.proto3.DoubleMessage")
	proto.RegisterType((*FloatMessage)(nil), "schema.proto3.FloatMessage")
}

func init() { proto.RegisterFile("floats.proto", fileDescriptor_floats_f5de057cb502e988) }

var fileDescriptor_floats_f5de057cb502e988 = []byte{
	// 119 bytes of a gzipped FileDescriptorProto
	0x1f, 0x8b, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0xff, 0xe2, 0xe2, 0x49, 0xcb, 0xc9, 0x4f,
	0x2c, 0x29, 0xd6, 0x2b, 0x28, 0xca, 0x2f, 0xc9, 0x17, 0xe2, 0x2d, 0x4e, 0xce, 0x48, 0xcd, 0x4d,
	0x84, 0xf0, 0x8c, 0x95, 0x6c, 0xb9, 0x78, 0x5d, 0xf2, 0x4b, 0x93, 0x72, 0x52, 0x7d, 0x53, 0x8b,
	0x8b, 0x13, 0xd3, 0x53, 0x85, 0x44, 0xb8, 0x58, 0xcb, 0x12, 0x73, 0x4a, 0x53, 0x25, 0x18, 0x15,
	0x18, 0x35, 0x18, 0x83, 0x20, 0x1c, 0x21, 0x31, 0x2e, 0x36, 0x30, 0xa3, 0x58, 0x82, 0x49, 0x81,
	0x59, 0x83, 0x31, 0x08, 0xca, 0x53, 0xb2, 0xe1, 0xe2, 0x71, 0x03, 0x99, 0x8e, 0x55, 0x37, 0x13,
	0x76, 0xdd, 0x4c, 0x30, 0xdd, 0x49, 0x6c, 0x10, 0x47, 0x00, 0x02, 0x00, 0x00, 0xff, 0xff, 0x5c,
	0x07, 0xe4, 0x41, 0xa2, 0x00, 0x00, 0x00,
}
